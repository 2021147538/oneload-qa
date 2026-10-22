"""Regression checks use a Backend model without importing its DB fixtures."""

import json
import os
import sys
from pathlib import Path

import pytest

QA_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(os.environ.get("QA_PROJECT_ROOT", QA_ROOT.parent)).resolve()
sys.path[:0] = [
    str(QA_ROOT / "scripts"),
    str(PROJECT_ROOT / "oneload-backend"),
    str(PROJECT_ROOT / "oneload_agent"),
]


@pytest.fixture
def seoul_json():
    return json.loads(
        (PROJECT_ROOT / "oneload-data/maps/seoul-station.json").read_text()
    )
