"""Run current QA checks and publish consistent, reviewed-format evidence without live AI."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from qa_inputs import (
    SOURCE_REPOS,
    InputError,
    inspect_data,
    load_live_map,
    resolve_map_dir,
    source_commits,
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def suite(path: Path) -> dict:
    node = ET.parse(path).getroot()
    nodes = [node] if node.tag == "testsuite" else node.findall("testsuite")
    if not nodes:
        raise ValueError("JUnit has no test suites")
    return {
        key: sum(int(item.get(key, "0")) for item in nodes)
        for key in ("tests", "failures", "errors", "skipped")
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--map-dir", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument(
        "--with-backend",
        action="store_true",
        help="Use a disposable Docker DB and real R2 API probes",
    )
    ap.add_argument(
        "--reports",
        type=Path,
        help="Update structured public evidence after all artifacts exist",
    )
    args = ap.parse_args()
    if args.reports and not args.with_backend:
        ap.error(
            "--reports requires --with-backend to avoid publishing partial baseline evidence"
        )
    root, out = args.project_root.resolve(), args.output.resolve()
    qa = Path(__file__).resolve().parent.parent
    scripts = qa / "scripts"
    for name in SOURCE_REPOS:
        if not (root / name / ".git").exists():
            ap.error("Expected sibling Git repository: " + name)
        if (
            args.reports
            and subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=root / name, text=True
            ).strip()
        ):
            ap.error("Public evidence requires a clean source checkout: " + name)
    sys.path.insert(0, str(root / "oneload-backend"))
    try:
        directory = resolve_map_dir(root, args.map_dir)
        _, initial_map = load_live_map(root, directory)
        initial_commits = source_commits(root)
    except InputError as exc:
        ap.error(str(exc))
    if out.exists() and any(out.iterdir()):
        ap.error("Use a new output directory; existing evidence is not overwritten")
    out.mkdir(parents=True, exist_ok=True)
    env = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        PYTEST_ADDOPTS="",
        MAP_DIR=str(directory),
        QA_PROJECT_ROOT=str(root),
        LANGSMITH_TRACING="false",
        LANGCHAIN_TRACING_V2="false",
    )
    steps = []

    def run(name, command, cwd):
        start = time.perf_counter()
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            (out / (name + ".log")).write_text(result.stdout, encoding="utf-8")
            code = result.returncode
        except OSError as exc:
            # Keep exception text and environment out of public evidence.
            (out / (name + ".log")).write_text(
                type(exc).__name__ + "\n", encoding="utf-8"
            )
            code = 127
        steps.append(
            {
                "name": name,
                "exit_code": code,
                "elapsed_s": round(time.perf_counter() - start, 3),
            }
        )
        print(f"{name}: exit {code}", flush=True)

    py = sys.executable
    run(
        "qa-tests",
        [
            py,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            str(qa / "tests"),
            "--junitxml=" + str(out / "qa-junit.xml"),
        ],
        qa,
    )
    run(
        "data-validation",
        [
            py,
            str(scripts / "validate_data.py"),
            "--project-root",
            str(root),
            "--map-dir",
            str(directory),
            "--output",
            str(out / "data-validation.json"),
        ],
        qa,
    )
    run(
        "agent-tests",
        [
            py,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--junitxml=" + str(out / "agent-junit.xml"),
        ],
        root / "oneload_agent",
    )
    run(
        "contract-audit",
        [
            py,
            str(scripts / "audit_contracts.py"),
            "--map-dir",
            str(directory),
            "--project-root",
            str(root),
            "--output",
            str(out / "contract-audit.json"),
        ],
        qa,
    )
    run(
        "component-eval",
        [
            py,
            str(scripts / "evaluate_agent.py"),
            "--map-dir",
            str(directory),
            "--project-root",
            str(root),
            "--cases",
            str(qa / "eval/component_cases.json"),
            "--mode",
            "fake",
            "--prompt-version",
            "v3",
            "--output",
            str(out / "component"),
        ],
        qa,
    )
    if args.with_backend:
        run(
            "backend-and-integration",
            [
                py,
                str(scripts / "run_backend_tests.py"),
                "--map-dir",
                str(directory),
                "--project-root",
                str(root),
                "--with-r2",
                "--output",
                str(out / "backend"),
            ],
            qa,
        )

    overall = 1 if any(step["exit_code"] != 0 for step in steps) else 0
    manifest = {
        "executed_at_kst": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        "steps": steps,
        "commits": initial_commits,
        "map": initial_map,
        "overall_exit_code": overall,
        "live_model_calls": 0,
        "with_backend": args.with_backend,
    }
    (out / "run.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not args.reports:
        return overall

    # A known upstream failure is publishable. Missing or malformed evidence is not.
    try:
        data_validation = load_json(out / "data-validation.json")
        audit = load_json(out / "contract-audit.json")
        component = load_json(out / "component/metadata.json")
        probe = load_json(out / "backend/integration-probe.json")
        backend_run = load_json(out / "backend/backend-run.json")
        qa_suite = suite(out / "qa-junit.xml")
        agent_suite, backend_suite = (
            suite(out / "agent-junit.xml"),
            suite(out / "backend/backend-junit.xml"),
        )
        commits = source_commits(root)
        if commits != initial_commits or any(
            report["commits"] != commits
            for report in (audit, component, probe, data_validation)
        ):
            raise ValueError("Source commits changed during checks")
        if any(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=root / name, text=True
            ).strip()
            for name in commits
        ):
            raise ValueError("Source working tree changed during checks")
        _, current_map = load_live_map(root, directory)
        if current_map != initial_map or any(
            report["map"] != current_map for report in (audit, component, probe)
        ):
            raise ValueError("Mixed live-map evidence")
        current_data = inspect_data(root, directory)
        if any(
            data_validation[key] != current_data[key]
            for key in ("checks", "maps", "asset_sha256")
        ):
            raise ValueError("Map schema or photo files changed during checks")
        if (
            hashlib.sha256((scripts / "evaluate_agent.py").read_bytes()).hexdigest()
            != component["runner_sha256"]
        ):
            raise ValueError("Component runner changed during checks")
        with (out / "component/results.csv").open(
            encoding="utf-8-sig", newline=""
        ) as file:
            if len(list(csv.DictReader(file))) != component["turn_count"]:
                raise ValueError("Component CSV/metadata count mismatch")
    except (OSError, ValueError, KeyError, ET.ParseError) as exc:
        print(
            "Public reports unchanged: incomplete or inconsistent evidence ("
            + type(exc).__name__
            + ")"
        )
        return 1

    report_dir = args.reports.resolve()
    previous = (
        load_json(report_dir / "baseline.json")
        if (report_dir / "baseline.json").exists()
        else {}
    )
    frontend = {
        "commit": commits["oneload-app"],
        "status": "not_run",
        "browser_e2e_executed": False,
    }
    old_front = previous.get("frontend", {})
    if old_front.get("commit") == commits["oneload-app"]:
        frontend = dict(
            old_front, scope="retained results from the same unchanged commit"
        )
    baseline = {
        "date": manifest["executed_at_kst"][:10],
        "executed_at_kst": manifest["executed_at_kst"],
        "commits": commits,
        "overall_exit_code": overall,
        "steps": steps,
        "map": current_map,
        "qa": {"suite": qa_suite},
        "data": {
            "passed": data_validation["passed"],
            "total": data_validation["total"],
            "maps": data_validation["maps"],
            "asset_sha256": data_validation["asset_sha256"],
            "validation_scope": data_validation["validation_scope"],
        },
        "agent": {
            "suite": agent_suite,
            "model": "FakeLLM",
            "checkout": "Local synchronized main",
        },
        "backend": {
            "suite": backend_suite,
            "run": backend_run,
            "environment": "disposable PostgreSQL 17; no production DB",
        },
        "component": {
            key: component[key]
            for key in (
                "dataset_version",
                "dataset_sha256",
                "auto_scenarios_passed",
                "scenario_count",
                "auto_turns_passed",
                "turn_count",
                "human_review_pending",
                "final_quality_score",
            )
        },
        "integration": {
            "passed": probe["passed"],
            "total": probe["total"],
            "failed": [c["id"] for c in probe["checks"] if not c["passed"]],
            "fixture": "FakeLLM, MockKnowledgeSearch, synthetic JPEG; explicit R2 injection",
        },
        "frontend": frontend,
        "real_llm_calls": 0,
        "field_photo_count": 0,
        "production_ai_quality_measured": False,
        "runner_hashes": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(scripts.glob("*.py"))
        },
    }
    report_dir.mkdir(parents=True, exist_ok=True)
    (out / "baseline.json").write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for source, name in (
        (out / "baseline.json", "baseline.json"),
        (out / "contract-audit.json", "contract-audit.json"),
        (out / "data-validation.json", "data-validation.json"),
        (out / "component/metadata.json", "component-metadata.json"),
        (out / "component/results.csv", "component-results.csv"),
        (out / "backend/integration-probe.json", "integration-probe.json"),
    ):
        temporary = report_dir / ("." + name + ".tmp")
        shutil.copyfile(source, temporary)
        temporary.replace(report_dir / name)
    print("Structured reports updated; nonzero upstream checks remain failures.")
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
