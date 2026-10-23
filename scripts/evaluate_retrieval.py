"""Select MemorySearch threshold on R6 dev; evaluate holdout and R3 diagnostic set."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import yaml
from qa_inputs import InputError, digest
from rag_inputs import load_rag


def validate_dataset(data, known_ids):
    cases = data["cases"]
    ids = [c["id"] for c in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ValueError("Cases must be nonempty with unique ids")
    for c in cases:
        if c["split"] not in {"dev", "holdout"} or c["lang"] not in {"ko", "en"}:
            raise ValueError("Invalid split or language")
        if not c["q"].strip() or not c["family"] or not set(c["gold"]) <= known_ids:
            raise ValueError("Invalid question, family, or gold document")
    for field in ("family", "q"):
        dev = {c[field] for c in cases if c["split"] == "dev"}
        holdout = {c[field] for c in cases if c["split"] == "holdout"}
        if dev & holdout:
            raise ValueError("Dev/holdout overlap: " + field)
    for split in ("dev", "holdout"):
        subset = [c for c in cases if c["split"] == split]
        if not any(c["gold"] for c in subset) or not any(not c["gold"] for c in subset):
            raise ValueError("Each split needs positive and out-of-scope cases")


def score(cases, search):
    rows = []
    for c in cases:
        hits = search(c["q"], c["lang"], {"slots": {"train_type": c.get("train")}})
        found = [h.document_id for h in hits]
        gold = set(c["gold"])
        rows.append(
            {
                "id": c["id"],
                "question": c["q"],
                "gold": c["gold"],
                "retrieved": found,
                "passed": bool(gold & set(found[:3])) if gold else not found,
            }
        )
    positive = [r for r in rows if r["gold"]]
    negative = [r for r in rows if not r["gold"]]
    tp = sum(r["passed"] for r in positive)
    fp = sum(not r["passed"] for r in negative)
    denominator = 2 * tp + len(positive) - tp + 2 * fp
    return {
        "positive_total": len(positive),
        "top1": sum(
            bool(r["retrieved"] and r["retrieved"][0] in r["gold"]) for r in positive
        ),
        "top3": tp,
        "out_of_scope_total": len(negative),
        "out_of_scope_empty": len(negative) - fp,
        "false_positives": fp,
        "objective": 2 * tp / denominator if denominator else 0.0,
        "rows": rows,
    }


def select_threshold(dev_cases, candidates, factory):
    # Reject holdout rows here so callers cannot accidentally optimize on holdout.
    if not dev_cases or any(c["split"] != "dev" for c in dev_cases):
        raise ValueError("Threshold selection accepts dev cases only")
    if not candidates or any(not 0 <= x <= 1 for x in candidates):
        raise ValueError("Threshold candidates must be within 0..1")
    table = [
        {"min_score": value, **score(dev_cases, factory(value))} for value in candidates
    ]
    selected = max(
        table, key=lambda r: (r["objective"], -r["false_positives"], -r["min_score"])
    )
    return selected["min_score"], table


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", required=True, type=Path)
    ap.add_argument(
        "--cases",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "eval/retrieval_cases.json",
    )
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    if args.output.exists():
        ap.error("Use a new report path")
    root = args.project_root.resolve()
    data = json.loads(args.cases.read_text())
    try:
        initial, metadata = load_rag(root)
        validate_dataset(data, set(metadata["document_ids"]))
        if (
            data["selection_policy"]["k"] != initial.k
            or data["selection_policy"]["relative_cutoff"]
            != metadata["relative_cutoff"]
        ):
            raise ValueError(
                "RAG search policy changed; version dataset before rerunning"
            )
    except (InputError, ValueError) as exc:
        ap.error(str(exc))
    from hangil_rag.search_memory import MemorySearch

    factory = lambda threshold: MemorySearch(
        docs=initial.docs, k=3, min_score=threshold
    )
    threshold, table = select_threshold(
        [c for c in data["cases"] if c["split"] == "dev"],
        data["selection_policy"]["candidates"],
        factory,
    )
    held = score(
        [c for c in data["cases"] if c["split"] == "holdout"], factory(threshold)
    )
    selected_dev = next(r for r in table if r["min_score"] == threshold)
    gate = data["selection_policy"]["release_gate"]
    acceptable = all(
        s["top3"] / s["positive_total"] >= gate["positive_top3_recall_min"]
        and s["false_positives"] <= gate["out_of_scope_false_positives_max"]
        for s in (selected_dev, held)
    )
    legacy_path = root / "oneload-rag/eval/retrieval.yaml"
    legacy = yaml.safe_load(legacy_path.read_text())["cases"]
    report = {
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "dataset_version": data["dataset_version"],
        "dataset_sha256": digest(args.cases),
        "runner_sha256": digest(Path(__file__)),
        "rag_inputs_sha256": digest(Path(__file__).with_name("rag_inputs.py")),
        "rag": metadata,
        "selection_policy": data["selection_policy"],
        "selected_min_score": threshold,
        "decision": "qa_candidate_accepted"
        if acceptable
        else "production_threshold_not_approved",
        "dev_sweep": table,
        "holdout": held,
        "r3_legacy": {
            "dataset_sha256": digest(legacy_path),
            "default_0_25": score(legacy, factory(0.25)),
            "selected": score(legacy, factory(threshold)),
        },
        "limitations": [
            "Synthetic R6 questions; same document corpus; small family-disjoint holdout",
            "Any-gold top3 does not measure citation precision or factual answer quality",
            "No live LLM, embeddings, pgvector, or production wiring tested",
            "If release gate fails, fix retrieval/scope detection and create a NEW holdout; do not tune on this holdout",
        ],
    }
    _, final_metadata = load_rag(root)
    if final_metadata != metadata:
        raise InputError("RAG input changed during evaluation; report not published")
    report["rag"]["min_score"] = threshold
    report["input_stability_checked"] = True
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {k: report[k] for k in ("selected_min_score", "decision")},
            ensure_ascii=False,
        )
    )
    print(
        f"holdout top3={held['top3']}/{held['positive_total']} OOS empty={held['out_of_scope_empty']}/{held['out_of_scope_total']}"
    )
    return 0 if acceptable else 1


if __name__ == "__main__":
    raise SystemExit(main())
