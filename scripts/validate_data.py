"""Validate oneload-data with current Backend models without changing any source."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from qa_inputs import InputError, inspect_data, source_commits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--map-dir", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.project_root.resolve()
    sys.path.insert(0, str(root / "oneload-backend"))
    try:
        commits = source_commits(root)
        report = inspect_data(root, args.map_dir)
    except InputError as exc:
        ap.error(str(exc))
    report.update(
        commits=commits, checked_at_kst=datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for check in report["checks"]:
        print(f"{check['id']}: {'PASS' if check['passed'] else 'FAIL'}")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
