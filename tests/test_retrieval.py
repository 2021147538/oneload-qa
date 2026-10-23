"""Guard independent threshold selection and positive/negative scoring semantics."""

import csv
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from evaluate_retrieval import score, select_threshold, validate_dataset
from qa_inputs import digest
from rag_inputs import load_rag

QA = Path(__file__).resolve().parents[1]


def case(id_, gold, split="dev", family=None):
    return {
        "id": id_,
        "q": id_,
        "lang": "en",
        "gold": gold,
        "split": split,
        "family": family or id_,
    }


def test_scoring_distinguishes_empty_from_wrong_document():
    cases = [case("pos", ["right"]), case("neg", [])]
    result = score(cases, lambda q, lang, ctx: [SimpleNamespace(document_id="wrong")])
    assert (result["top3"], result["false_positives"], result["objective"]) == (0, 1, 0)
    result = score(
        cases,
        lambda q, lang, ctx: (
            [SimpleNamespace(document_id="right")] if q == "pos" else []
        ),
    )
    assert (
        result["top1"],
        result["top3"],
        result["out_of_scope_empty"],
        result["objective"],
    ) == (1, 1, 1, 1)


def test_selection_penalizes_false_positives_and_breaks_ties():
    cases = [case("pos", ["right"]), case("neg", [])]

    def factory(threshold):
        return lambda q, lang, ctx: (
            [SimpleNamespace(document_id="right")]
            if q == "pos" or threshold < 0.3
            else []
        )

    threshold, _ = select_threshold(cases, [0.2, 0.4, 0.3], factory)
    assert threshold == 0.3


def test_holdout_cannot_select_threshold():
    with pytest.raises(ValueError, match="dev cases only"):
        select_threshold([case("held", [], "holdout")], [0.25], lambda _: None)


def test_family_leakage_and_unknown_gold_rejected():
    data = {
        "cases": [
            case("d1", ["right"], family="shared"),
            case("d2", []),
            case("h1", ["right"], "holdout", "shared"),
            case("h2", [], "holdout"),
        ]
    }
    with pytest.raises(ValueError, match="overlap"):
        validate_dataset(data, {"right"})
    data["cases"][2]["family"] = "new"
    validate_dataset(data, {"right"})
    with pytest.raises(ValueError, match="gold"):
        validate_dataset(data, set())


def test_missing_rag_fails_before_docker(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(QA / "scripts/run_backend_tests.py"),
            "--project-root",
            str(tmp_path),
            "--with-rag",
            "--output",
            str(tmp_path / "out"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "requires sibling oneload-rag" in result.stderr
    assert not (tmp_path / "out").exists()
    with pytest.raises(ValueError, match="requires sibling"):
        load_rag(tmp_path)


def test_service_v2_keeps_human_review_pending_and_versions_fare_change():
    rows = list(
        csv.DictReader((QA / "eval/service_gold.csv").open(encoding="utf-8-sig"))
    )
    old = list(
        csv.DictReader(
            (QA / "eval/archive/service_gold-v1.csv").open(encoding="utf-8-sig")
        )
    )
    meta = json.loads((QA / "eval/service_gold.meta.json").read_text())
    fare = next(r for r in rows if r["id"] == "Q10")
    assert next(r for r in old if r["id"] == "Q10")["type"] == "답불가"
    assert fare["type"] == "답가능" and "verified_at" in fare["expected_behavior"]
    assert "doc-fare-arex-express" in fare["source_doc"]
    assert meta["sha256"] == digest(QA / "eval/service_gold.csv")
    assert len(rows) == len(old) == meta["rows"] == 20
    assert all(
        r["source_doc"]
        and r["source_locator"]
        and r["ground_truth_status"] == "mapped_pending_human_review"
        for r in rows
    )
    assert all(
        not r[k] for r in rows for k in ("actual_output", "auto_pass", "human_pass")
    )
