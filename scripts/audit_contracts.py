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

from frontend_wiring import inspect_frontend
from production_wiring import probe_entrypoint
from qa_inputs import InputError, digest, load_live_map, source_commits


def probe_vision_failure(
    vision, backend_exception: type[Exception]
) -> tuple[bool, dict]:
    """Check the exception actually thrown, using Backend's except semantics."""
    evidence = {
        "input": "synthetic bytes; no live model",
        "expected_exception": f"{backend_exception.__module__}.{backend_exception.__qualname__}",
        "http_reproduction": "run_backend_tests.py --with-r2 / INT-08-vision-down",
    }
    try:
        vision.extract(b"synthetic")
    except backend_exception as exc:
        caught = True
        evidence["outcome"] = "expected_exception"
        evidence["actual_exception"] = (
            f"{type(exc).__module__}.{type(exc).__qualname__}"
        )
    except Exception as exc:  # noqa: BLE001 - Unexpected types must fail with evidence.
        caught = False
        evidence["outcome"] = "unexpected_exception"
        evidence["actual_exception"] = (
            f"{type(exc).__module__}.{type(exc).__qualname__}"
        )
    else:
        caught = False
        evidence["outcome"] = "no_exception"
        evidence["actual_exception"] = None
    evidence["backend_caught"] = caught
    return caught, evidence


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
    try:
        frontend = inspect_frontend(
            root / "oneload-app",
            Path(__file__).resolve().parents[1] / "eval/frontend_wiring.json",
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        ap.error("Invalid Frontend review registry: " + type(exc).__name__)
    checks.append(
        {
            "id": "INT-06",
            "passed": True
            if frontend["status"] == "wired"
            else False
            if frontend["status"] == "incomplete"
            else None,
            "status": frontend["status"],
            "validation_level": "reviewed_source_only",
            "evidence": frontend,
        }
    )
    if frontend["status"] != "wired":
        incomplete = frontend["status"] == "incomplete"
        add(
            "INT-06",
            "P0" if incomplete else "review_required",
            "Reviewed Frontend source has incomplete HTTP flows"
            if incomplete
            else "Frontend runtime source changed; call-path review required",
            frontend,
        )
    production = probe_entrypoint(root / "oneload-backend/app/main.py")
    checks.append(
        {
            "id": "INT-07",
            "passed": False,
            "status": "partial"
            if production["agent_vision_conditionally_wired"]
            else "incomplete",
            "validation_level": "actual_entrypoint_with_fake_provider",
            "evidence": production,
        }
    )
    if not production["agent_vision_conditionally_wired"]:
        add(
            "INT-07",
            "P0",
            "Backend entrypoint does not select shared R2 Agent/Vision when a key is present",
            production,
        )
    elif production["production_knowledge_is_demo"]:
        add(
            "INT-07",
            "P0",
            "R2 Agent/Vision selection is wired; production knowledge still uses MockKnowledgeSearch",
            production,
        )
    else:
        add(
            "INT-07",
            "review_required",
            "Agent/Vision selection is wired; production search needs independent provenance/API review",
            production,
        )
    caught, evidence = probe_vision_failure(
        LLMVision(FakeLLM(down=True)), backend.VisionUnavailable
    )
    check("INT-08", caught, evidence)
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
        "scope": "Real Backend context/map/guard + FakeLLM; actual Vision failure, schemas and static wiring; no live models",
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
        print(
            f"{item['id']}: {'REVIEW_REQUIRED' if item['passed'] is None else 'PASS' if item['passed'] else 'FAIL'}"
        )
    for item in findings:
        print(f"{item['id']} [{item['severity']}] {item['description']}")
    return 1 if any(f["severity"] in {"P0", "review_required"} for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
