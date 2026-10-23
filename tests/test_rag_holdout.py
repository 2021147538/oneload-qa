"""Protect the frozen holdout from leakage or parameter changes before execution."""

import copy

import pytest
from recheck_rag_issue3 import validate_holdout


def valid():
    return {
        "protocol": {"primary_min_score": 0.25, "k": 3, "relative_cutoff": 0.5},
        "cases": [
            {
                "id": "p",
                "q": "new ticket question",
                "lang": "en",
                "family": "ticket",
                "gold": ["doc-ticket"],
            },
            {
                "id": "n",
                "q": "new unrelated question",
                "lang": "en",
                "family": "other",
                "gold": [],
            },
        ],
    }


def test_fresh_holdout_accepts_fixed_protocol():
    validate_holdout(
        valid(), {"search_outputs_seen_at_freeze": False}, {"doc-ticket"}, set()
    )


@pytest.mark.parametrize(
    "mutation", ["leak", "duplicate", "threshold", "unknown_gold", "seen"]
)
def test_holdout_rejects_leakage_and_changed_policy(mutation):
    data, meta, exposed = (
        copy.deepcopy(valid()),
        {"search_outputs_seen_at_freeze": False},
        set(),
    )
    if mutation == "leak":
        exposed.add("new ticket question")
    if mutation == "duplicate":
        data["cases"][1]["q"] = data["cases"][0]["q"]
    if mutation == "threshold":
        data["protocol"]["primary_min_score"] = 0.35
    if mutation == "unknown_gold":
        data["cases"][0]["gold"] = ["doc-not-present"]
    if mutation == "seen":
        meta["search_outputs_seen_at_freeze"] = True
    with pytest.raises(ValueError):
        validate_holdout(data, meta, {"doc-ticket"}, exposed)
