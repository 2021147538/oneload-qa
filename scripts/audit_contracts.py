"""Audit current contracts without modifying team repositories or calling live models."""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import get_args
from zoneinfo import ZoneInfo

from qa_inputs import InputError, digest, load_live_map, source_commits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--map-dir", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.project_root.resolve()
    sys.path[:0] = [str(root / "oneload-backend"), str(root / "oneload_agent")]
    from app.ai import contracts as backend
    from app.ai.guard import guard
    from app.domain import localization as loc
    from hangil_r2 import FakeLLM, LLMAgent, LLMVision, MockKnowledgeSearch
    from hangil_r2.backend import contracts as r2
    from hangil_r2.backend import localization_types as r2loc

    try:
        map_, map_info = load_live_map(root, args.map_dir)
        commits = source_commits(root)
    except InputError as exc:
        ap.error(str(exc))
    checks, findings = [], []

    def check(id_, passed, evidence):
        checks.append({"id": id_, "passed": bool(passed), "evidence": evidence})
        if not passed:
            findings.append(
                {
                    "id": id_,
                    "severity": "P0",
                    "description": "Contract regression",
                    "evidence": evidence,
                }
            )

    def add(id_, severity, description, evidence):
        findings.append(
            {
                "id": id_,
                "severity": severity,
                "description": description,
                "evidence": evidence,
            }
        )

    bparams = list(inspect.signature(backend.Agent.handle_message).parameters)[1:]
    aparams = list(inspect.signature(LLMAgent.handle_message).parameters)[1:]
    ctx = backend.AgentContext(
        language="ko",
        map=map_,
        state="needs_clarification",
        destination_poi_id=None,
        confirmed_node_id=None,
        slots=backend.Slots(train_type="allstop"),
    )
    result = LLMAgent(FakeLLM(), search_knowledge=MockKnowledgeSearch()).handle_message(
        ctx, "없어요", None, None
    )
    response = guard(result, map_, "ko")
    check(
        "INT-01",
        bparams == aparams and hasattr(result, "retrieved_document_ids"),
        {
            "backend_parameters": bparams,
            "r2_parameters": aparams,
            "return_wrapper": type(result).__name__,
        },
    )
    mismatches = [
        name
        for name in (
            "AgentResponse",
            "Slots",
            "Source",
            "SuggestedReply",
            "Destination",
        )
        if getattr(backend, name).model_json_schema()
        != getattr(r2, name).model_json_schema()
    ]
    mismatches += [
        name
        for name in ("Intent", "ReplyStatus", "NextAction", "TrainSlot", "CardSlot")
        if get_args(getattr(backend, name)) != get_args(getattr(r2, name))
    ]
    mismatches += [
        name
        for name in ("VisionFeatures", "VisionText", "Candidate")
        if getattr(loc, name).model_json_schema()
        != getattr(r2loc, name).model_json_schema()
    ]
    check("INT-02", not mismatches, {"schema_enum_mismatches": mismatches})
    check(
        "INT-03",
        response.slots.train_type == "allstop",
        {"actual_train_type": response.slots.train_type},
    )
    check(
        "INT-04",
        response.destination is not None
        and response.destination.poi_id == "poi-allstop-tickets"
        and response.slots.has_transit_card == "no",
        {
            "context_class": "Backend AgentContext/Slots",
            "follow_up": "없어요",
            "response": response.model_dump(mode="json"),
        },
    )
    features = LLMVision(
        FakeLLM(scene={"image_quality": "usable", "texts": [{"text": "4호선"}]})
    ).extract(b"synthetic")
    candidates = loc.match_location(features, map_, loc.Hints(), "ko")
    # A survey update may legitimately differ from the frozen Agent fixture.
    same_map = map_info["sha256"] == digest(
        root / "oneload_agent/mocks/maps/seoul-station.json"
    )
    check(
        "INT-05",
        bool(candidates),
        {
            "live_map_matches_agent_fixture": same_map,
            "backend_candidates": [c.node_id for c in candidates],
        },
    )
    store = (root / "oneload-app/src/store.tsx").read_text()
    if "const AI_DELAY_MS" in store and "SCENARIOS[p.scenario]" in store:
        add(
            "INT-06",
            "P0",
            "Frontend still executes local mock flows",
            ["oneload-app/src/store.tsx", "oneload-app/README.md"],
        )
    source = (root / "oneload-backend/app/main.py").read_text()
    if (
        "app = create_app()" in source
        and "agent or RuleAgent()" in source
        and "vision or NoVision()" in source
    ):
        add(
            "INT-07",
            "P0",
            "Backend production entry point uses RuleAgent/NoVision",
            {
                "file": "oneload-backend/app/main.py",
                "r2_injected_probe_is_not_production_wiring": True,
            },
        )
    if not issubclass(r2.VisionUnavailable, backend.VisionUnavailable):
        add(
            "INT-08",
            "P0",
            "R2 raises a different VisionUnavailable class; Backend handler cannot catch it",
            {
                "r2_exception": r2.VisionUnavailable.__module__,
                "backend_exception": backend.VisionUnavailable.__module__,
                "identity_matches": False,
                "http_reproduction": "run_backend_tests.py --with-r2 / INT-08-vision-down",
            },
        )
    graph = map_.model_dump(mode="json")
    if any(p.get("is_example") for p in graph.get("panoramas", [])):
        add(
            "DATA-01",
            "release_gate",
            "Example panoramas and draft map/knowledge need official and field verification",
            {
                "map_id": map_.map_id,
                "example_panorama_count": sum(
                    bool(p.get("is_example")) for p in graph["panoramas"]
                ),
            },
        )
    report = {
        "checked_at_kst": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        "scope": "Real Backend context/map/guard + FakeLLM; schemas and static wiring; no live models",
        "commits": commits,
        "map": map_info,
        "contract_checks": checks,
        "findings": findings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for item in checks:
        print(f"{item['id']}: {'PASS' if item['passed'] else 'FAIL'}")
    for item in findings:
        print(f"{item['id']} [{item['severity']}] {item['description']}")
    return 1 if any(f["severity"] == "P0" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
