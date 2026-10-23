"""A new Backend package dependency must fail preflight before creating any DB."""

import subprocess
import sys
from pathlib import Path


def test_backend_missing_agent_fails_before_docker(tmp_path):
    repo = tmp_path / "oneload-backend"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests/conftest.py").write_text("")
    (repo / "pyproject.toml").write_text(
        '[project]\ndependencies = ["oneload-agent"]\n'
    )
    output = tmp_path / "not-created"
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts/run_backend_tests.py"),
            "--project-root",
            str(tmp_path),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "requires sibling oneload_agent" in result.stderr
    assert not output.exists()
