"""Evaluate R2 using real Backend context/map/guard. Mock checks are not AI accuracy."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from qa_inputs import InputError, load_live_map, source_commits


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def agent_assets(repo, version, prompt_dir, mock_dir, *, requires_verify=False):
    """Record the assets the imported Agent actually reads, including packages."""
    repo, prompt_dir, mock_dir = (
        Path(path).resolve() for path in (repo, prompt_dir, mock_dir)
    )
    if any(not path.is_relative_to(repo) for path in (prompt_dir, mock_dir)):
        raise InputError("Imported Agent assets must belong to the selected checkout")
    roles = ("understand", "compose", "scene") + (
        ("verify",) if requires_verify else ()
    )
    prompts = [prompt_dir / f"{name}_{version}.md" for name in roles]
    if any(not path.is_file() for path in prompts):
        raise InputError(
            "Requested prompt version must include files for: " + ", ".join(roles)
        )
    mocks = sorted(mock_dir.rglob("*.json"))
    if not (mock_dir / "knowledge.json").is_file():
        raise InputError("Imported Agent mock knowledge.json is missing")
    return prompts, mocks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--map-dir", type=Path)
    ap.add_argument("--cases", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--mode", choices=["fake", "openai"], default="fake")
    ap.add_argument("--prompt-version", help="Default: selected Agent's code default")
    args = ap.parse_args()
    root = args.project_root.resolve()
    repo, backend = root / "oneload_agent", root / "oneload-backend"
    sys.path[:0] = [str(backend), str(repo)]
    try:
        map_, map_info = load_live_map(root, args.map_dir)
        commits = source_commits(root)
    except InputError as exc:
        ap.error(str(exc))
    scenarios = json.loads(args.cases.read_text(encoding="utf-8"))
    ids = [case["id"] for case in scenarios]
    if not ids or len(ids) != len(set(ids)):
        ap.error("Dataset must be nonempty and IDs unique")
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()):
        ap.error("Use a new output directory; evidence is not overwritten")
    out.mkdir(parents=True, exist_ok=True)
    os.environ.pop("PROMPT_VERSION", None)
    os.environ.update(
        LANGSMITH_TRACING="false",
        LANGCHAIN_TRACING_V2="false",
    )
    sys.path[:0] = [str(backend), str(repo)]
    from app.ai.contracts import AgentContext, Slots
    from app.ai.guard import guard
    from hangil_r2 import (
        FakeLLM,
        LLMAgent,
        MockKnowledgeSearch,
        OpenAILLM,
        ToolUnavailable,
    )
    from hangil_r2.knowledge import MOCK_DIR
    from hangil_r2.llm import LLM, PROMPT_DIR, prompt_version

    args.prompt_version = args.prompt_version or prompt_version()
    os.environ["PROMPT_VERSION"] = args.prompt_version

    try:
        required_prompts, mock_files = agent_assets(
            repo,
            args.prompt_version,
            PROMPT_DIR,
            MOCK_DIR,
            requires_verify=hasattr(LLM, "verify"),
        )
    except InputError as exc:
        ap.error(str(exc))

    rows = []
    for scenario in scenarios:
        retrieved = set()
        knowledge = MockKnowledgeSearch()

        def search(
            query,
            language,
            context,
            _scenario=scenario,
            _knowledge=knowledge,
            _retrieved=retrieved,
        ):
            fixture = _scenario.get("knowledge_fixture", "mock")
            if fixture == "down":
                raise ToolUnavailable("R6 injected outage")
            hits = [] if fixture == "empty" else _knowledge(query, language, context)
            _retrieved.update(hit.document_id for hit in hits)
            return hits

        forced = scenario.get("model_fixture") == "broken"
        llm = (
            FakeLLM(broken=True)
            if forced
            else FakeLLM()
            if args.mode == "fake"
            else OpenAILLM()
        )
        agent = LLMAgent(llm, search_knowledge=search)
        initial = scenario.get("initial_context", {})
        ctx = AgentContext(
            language=scenario["language"],
            map=map_,
            state="idle",
            destination_poi_id=None,
            confirmed_node_id=initial.get("confirmed_node_id"),
            slots=Slots(**initial.get("slots", {})),
        )
        for turn, case in enumerate(scenario["steps"], 1):
            retrieved.clear()
            start = time.perf_counter()
            response, error, payload, traced = None, "", {}, set()
            try:
                result = agent.handle_message(
                    ctx, case["message"], None, case.get("selected_poi_id")
                )
                traced = set(result.retrieved_document_ids)
                response = guard(result, map_, ctx.language)
                payload = response.model_dump(mode="json")
                actual = response.status
            except Exception as exc:  # noqa: BLE001 -- record failed cases and continue the dataset
                error = type(exc).__name__
                actual = "error:" + error
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            poi_id = (payload.get("destination") or {}).get("poi_id", "")
            sources = [source["document_id"] for source in payload.get("sources", [])]
            checks = {
                "status": actual in case["expected_status"],
                "poi": poi_id == case.get("expected_poi_id", ""),
                "cited_sources_retrieved": set(sources) <= retrieved
                and set(sources) <= traced,
                "answered_has_source": actual != "answered" or bool(sources),
                "destination_verified_map": not poi_id
                or map_.verified_poi(poi_id) is not None,
                "next_action": "expected_next_action" not in case
                or payload.get("next_action") == case["expected_next_action"],
                "slots": all(
                    payload.get("slots", {}).get(k) == v
                    for k, v in case.get("expected_slots", {}).items()
                ),
            }
            passed = all(checks.values())
            rows.append(
                {
                    "id": scenario["id"],
                    "turn": turn,
                    "type": scenario["type"],
                    "language": ctx.language,
                    "message": case["message"],
                    "expected_behavior": case["expected_behavior"],
                    "expected_status": "|".join(case["expected_status"]),
                    "actual_status": actual,
                    "poi_id": poi_id,
                    "source_ids": "|".join(sources),
                    "auto_pass": passed,
                    "human_pass": "",
                    "human_notes": "",
                    "failed_checks": "|".join(k for k, v in checks.items() if not v),
                    "latency_ms": elapsed,
                    "response_json": json.dumps(payload, ensure_ascii=False),
                    "execution_mode": "stubbed_model_failure" if forced else args.mode,
                    "tool_mode": scenario.get("knowledge_fixture", "mock"),
                    "error_type": error,
                }
            )
            if response is not None:
                here = None if actual == "relocalize" else ctx.confirmed_node_id
                state = ctx.state
                if actual == "destination_set":
                    state = "ready_to_navigate" if here else "needs_location"
                elif actual == "needs_clarification":
                    state = "needs_clarification"
                elif actual == "relocalize":
                    state = "needs_location"
                ctx = replace(
                    ctx,
                    state=state,
                    confirmed_node_id=here,
                    slots=Slots.model_validate(payload["slots"]),
                    destination_poi_id=poi_id or ctx.destination_poi_id,
                    recent_messages=[
                        *ctx.recent_messages,
                        ("user", case["message"]),
                        ("assistant", response.assistant_message),
                    ][-6:],
                )
            print(f"{scenario['id']}/{turn}: {'PASS' if passed else 'FAIL'} {actual}")

    with (out / "results.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    passed_scenarios = sum(
        all(row["auto_pass"] for row in rows if row["id"] == id_) for id_ in ids
    )
    latencies = sorted(row["latency_ms"] for row in rows)
    metadata = {
        "executed_at_kst": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        "dataset_version": "r6-component-v2",
        "dataset_sha256": digest(args.cases),
        "runner_sha256": digest(Path(__file__)),
        "commits": commits,
        "map": map_info,
        "python": sys.version.split()[0],
        "model_mode": args.mode,
        "model_name": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if args.mode == "openai"
        else "FakeLLM",
        "prompt_version": args.prompt_version,
        "prompt_hashes": {p.name: digest(p) for p in required_prompts},
        "prompt_directory": str(PROMPT_DIR.resolve().relative_to(repo)),
        "fixture_directory": str(MOCK_DIR.resolve().relative_to(repo)),
        "fixture_hashes": {str(p.relative_to(repo)): digest(p) for p in mock_files},
        "tools": "R2 MockKnowledgeSearch; real Backend map/context/guard; no production RAG",
        "scenario_count": len(ids),
        "turn_count": len(rows),
        "auto_scenarios_passed": passed_scenarios,
        "auto_turns_passed": sum(row["auto_pass"] for row in rows),
        "human_review_pending": len(rows),
        "final_quality_score": None,
        "p95_latency_ms_nearest_rank": latencies[math.ceil(len(latencies) * 0.95) - 1],
        "latency_scope": "component and selected model mode; not browser/API latency",
    }
    (out / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Automatic checks: {passed_scenarios}/{len(ids)} scenarios; human review pending."
    )
    return 0 if passed_scenarios == len(ids) else 1


if __name__ == "__main__":
    raise SystemExit(main())
