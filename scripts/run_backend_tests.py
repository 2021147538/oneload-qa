"""Run the existing Backend suite against a disposable, loopback-only PostgreSQL.

Never reads DATABASE_URL or TEST_DATABASE_URL from the caller. The upstream fixture
drops the public schema; only the database created by this process is passed to it.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from qa_inputs import InputError, digest, load_live_map, resolve_map_dir


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--map-dir", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument(
        "--with-r2",
        action="store_true",
        help="Also run real R2/Backend boundary probes with FakeLLM",
    )
    args = ap.parse_args()
    repo = args.project_root.resolve() / "oneload-backend"
    if not (repo / "tests/conftest.py").is_file():
        ap.error("oneload-backend/tests/conftest.py not found")
    root = args.project_root.resolve()
    sys.path.insert(0, str(repo))
    try:
        directory = (
            resolve_map_dir(root, args.map_dir)
            if args.with_r2
            else repo / "tests/fixtures/maps"
        )
        if args.with_r2:
            load_live_map(root, directory)
    except InputError as exc:
        ap.error(str(exc))
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()):
        ap.error("Use a new output directory; existing evidence is not overwritten")
    out.mkdir(parents=True, exist_ok=True)
    name = "hangil-r6-" + uuid.uuid4().hex[:10]
    dbname = "hangil_r6_test"
    password = uuid.uuid4().hex
    created = False
    start = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    try:
        subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-d",
                "--name",
                name,
                "-e",
                "POSTGRES_USER=hangil_r6",
                "-e",
                "POSTGRES_PASSWORD=" + password,
                "-e",
                "POSTGRES_DB=" + dbname,
                "-p",
                "127.0.0.1::5432",
                "pgvector/pgvector:pg17",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        created = True
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            ready = subprocess.run(
                ["docker", "exec", name, "pg_isready", "-U", "hangil_r6", "-d", dbname],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if ready.returncode == 0:
                break
            time.sleep(0.5)
        else:
            raise RuntimeError("Disposable PostgreSQL did not become ready")
        address = subprocess.check_output(
            ["docker", "port", name, "5432/tcp"], text=True
        ).strip()
        port = address.rsplit(":", 1)[1]
        url = f"postgresql+psycopg://hangil_r6:{password}@127.0.0.1:{port}/{dbname}"
        env = dict(
            os.environ,
            DATABASE_URL=url,
            TEST_DATABASE_URL=url,
            MAP_DIR=str(directory),
            PYTHONDONTWRITEBYTECODE="1",
            PYTEST_ADDOPTS="",
            LANGSMITH_TRACING="false",
            LANGCHAIN_TRACING_V2="false",
        )
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "--junitxml=" + str(out / "backend-junit.xml"),
            ],
            check=False,
            cwd=repo,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        log = result.stdout.replace(password, "[LOCAL_TEST_PASSWORD]")
        (out / "backend-tests.log").write_text(log, encoding="utf-8")
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo, text=True
        ).strip()
        (out / "backend-run.json").write_text(
            json.dumps(
                {
                    "started_at_kst": start,
                    "repository": "oneload-backend",
                    "commit": commit,
                    "python": sys.version.split()[0],
                    "exit_code": result.returncode,
                    "unit_fixture": {
                        "path": "tests/fixtures/maps/seoul-station.json",
                        "sha256": digest(
                            repo / "tests/fixtures/maps/seoul-station.json"
                        ),
                    },
                    "database": "disposable PostgreSQL 17; loopback; removed after run",
                    "ai_mode": "RuleAgent and test FakeVision; no live LLM/VLM",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(log)
        if args.with_r2 and result.returncode == 0:
            env["R6_DISPOSABLE_DB"] = "1"
            probe = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("probe_integration.py")),
                    "--project-root",
                    str(args.project_root.resolve()),
                    "--output",
                    str(out / "integration-probe.json"),
                    "--map-dir",
                    str(directory),
                ],
                check=False,
                cwd=repo,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            probe_log = probe.stdout.replace(password, "[LOCAL_TEST_PASSWORD]")
            (out / "integration-probe.log").write_text(probe_log, encoding="utf-8")
            print(probe_log)
            return probe.returncode
        return result.returncode
    finally:
        if created:
            subprocess.run(
                ["docker", "stop", "--time", "2", name],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


if __name__ == "__main__":
    raise SystemExit(main())
