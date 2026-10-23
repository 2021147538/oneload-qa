"""Probe real R2/Backend boundaries; invoked only by the disposable DB runner."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from qa_inputs import InputError, digest, load_live_map, resolve_map_dir, source_commits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--map-dir", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--knowledge", choices=("mock", "rag"), default="mock")
    ap.add_argument("--rag-min-score", type=float, default=0.25)
    args = ap.parse_args()
    url = urlparse(os.environ.get("DATABASE_URL", ""))
    if (
        url.hostname != "127.0.0.1"
        or url.path != "/hangil_r6_test"
        or url.username != "hangil_r6"
        or os.environ.get("R6_DISPOSABLE_DB") != "1"
    ):
        ap.error(
            "Use run_backend_tests.py --with-r2; a disposable loopback DB is required"
        )
    root = args.project_root.resolve()
    sys.path[:0] = [str(root / "oneload-backend"), str(root / "oneload_agent")]
    try:
        directory = resolve_map_dir(root, args.map_dir)
        _, map_info = load_live_map(root, directory)
        commits = source_commits(root)
    except InputError as exc:
        ap.error(str(exc))
    os.environ["MAP_DIR"] = str(directory)
    from app.ai.rule_agent import RuleAgent
    from app.main import create_app
    from fastapi.testclient import TestClient
    from hangil_r2 import FakeLLM, LLMAgent, LLMVision, MockKnowledgeSearch

    knowledge = MockKnowledgeSearch()
    rag_metadata = None
    if args.knowledge == "rag":
        from rag_inputs import load_rag

        try:
            knowledge, rag_metadata = load_rag(root, args.rag_min_score)
        except InputError as exc:
            ap.error(str(exc))

    checks = []
    jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 64

    def check(id_, expected, actual):
        checks.append(
            {
                "id": id_,
                "passed": actual == expected,
                "expected": expected,
                "actual": actual,
            }
        )
        print(f"{id_}: {'PASS' if actual == expected else 'FAIL'}")

    class Api:
        def __init__(self, http):
            self.http = http
            response = self.post(
                "/sessions",
                {
                    "language": "ko",
                    "map_id": "seoul-station",
                    "client": {"platform": "web", "app_version": "r6-fake-integration"},
                },
                auth=False,
            )
            body = response.json()
            self.sid, self.token, self.version = (
                body["session_id"],
                body["session_token"],
                body["map_version"],
            )

        def post(self, path, body=None, auth=True, **kw):
            headers = {"Idempotency-Key": str(uuid.uuid4())}
            if auth:
                headers["Authorization"] = "Bearer " + self.token
                path = "/sessions/" + self.sid + path
            return self.http.post("/api/v1" + path, headers=headers, json=body, **kw)

        def say(self, message):
            response = self.post("/messages", {"message": message})
            if response.status_code != 200:
                raise RuntimeError("Message HTTP " + str(response.status_code))
            return response.json()

        def photo(self):
            return self.post(
                "/localizations",
                data={"map_version": self.version},
                files={"image": ("synthetic.jpg", jpeg, "image/jpeg")},
            )

    llm = FakeLLM(
        scene={
            "image_quality": "usable",
            "texts": [
                {"text": "공항철도", "kind": "line_name"},
                {"text": "4호선", "kind": "line_number"},
            ],
        }
    )
    vision = LLMVision(llm)
    agent = LLMAgent(
        llm, search_knowledge=knowledge, vision=vision, fallback=RuleAgent()
    )
    with TestClient(
        create_app(agent=agent, vision=vision), raise_server_exceptions=False
    ) as http:
        api = Api(http)
        vague = api.say("공항 가는 티켓 어디서 사?")
        check("API-01-train-clarification", "needs_clarification", vague["status"])
        card = api.say("일반열차")
        check(
            "API-02-card-clarification",
            {"status": "needs_clarification", "train_type": "allstop"},
            {"status": card["status"], "train_type": card["slots"]["train_type"]},
        )
        ticket = api.say("없어요")
        check(
            "API-03-persisted-slots",
            {"poi": "poi-allstop-tickets", "card": "no", "state": "needs_location"},
            {
                "poi": ticket["destination"]["poi_id"],
                "card": ticket["slots"]["has_transit_card"],
                "state": ticket["session"]["state"],
            },
        )
        located = api.photo()
        check("API-04-photo-boundary", 200, located.status_code)
        body = located.json()
        check(
            "API-05-location-candidate",
            {"status": "needs_confirmation", "first": "line4-gates"},
            {
                "status": body["status"],
                "first": body["candidates"][0]["node_id"]
                if body["candidates"]
                else None,
            },
        )
        confirmed = api.post(
            "/location-confirmations",
            {
                "expected_revision": body["session"]["revision"],
                "method": "photo_candidate",
                "localization_id": body["localization_id"],
                "selected_node_id": "line4-gates",
            },
        )
        check(
            "API-06-confirmation",
            {"http": 200, "state": "ready_to_navigate"},
            {
                "http": confirmed.status_code,
                "state": confirmed.json().get("session", {}).get("state"),
            },
        )
        route = api.post(
            "/routes",
            {
                "expected_revision": confirmed.json()["session"]["revision"],
                "destination_poi_id": "poi-allstop-tickets",
                "map_version": api.version,
            },
        )
        r = route.json()
        check(
            "API-07-registered-route",
            {"http": 200, "start": "line4-gates", "goal": "allstop-tickets"},
            {
                "http": route.status_code,
                "start": r["path_node_ids"][0],
                "goal": r["path_node_ids"][-1],
            },
        )
        for event, target in [
            ("navigation_started", "navigating"),
            ("arrived", "arrived"),
        ]:
            response = api.post(
                "/navigation-events",
                {
                    "route_id": r["route_id"],
                    "events": [
                        {
                            "event_id": str(uuid.uuid4()),
                            "type": event,
                            "client_timestamp": datetime.now(UTC).isoformat(),
                        }
                    ],
                },
            )
            check(
                "API-08-" + event,
                {"http": 200, "state": target},
                {
                    "http": response.status_code,
                    "state": response.json().get("session", {}).get("state"),
                },
            )

    # FAQ Q7/Q8/Q9: exercise branches through real persisted sessions.
    with TestClient(
        create_app(agent=agent, vision=vision), raise_server_exceptions=False
    ) as http:
        api = Api(http)
        api.say("일반열차")
        card_yes = api.say("교통카드 있어요")
        check(
            "API-10-card-present",
            {"poi": "poi-allstop-platform", "card": "yes"},
            {
                "poi": (card_yes.get("destination") or {}).get("poi_id"),
                "card": card_yes["slots"]["has_transit_card"],
            },
        )
        express = Api(http).say("Where do I buy an express ticket?")
        check(
            "API-11-express-english",
            "poi-express-tickets",
            (express.get("destination") or {}).get("poi_id"),
        )
        unsure = Api(http).say("잘 모르겠어요")
        check(
            "API-12-unsure-without-timetable",
            {
                "status": "needs_clarification",
                "has_comparison_source": True,
                "items": [],
            },
            {
                "status": unsure["status"],
                "has_comparison_source": any(
                    x["document_id"] == "doc-arex-train-types"
                    for x in unsure["sources"]
                ),
                "items": unsure["items"],
            },
        )
        fare = Api(http).say("직통열차 요금 얼마야?")
        if args.knowledge == "rag":
            fare_sources = [
                x
                for x in fare["sources"]
                if x["document_id"] == "doc-fare-arex-express"
            ]
            check(
                "API-13-fare-with-rag-evidence",
                {"status": "answered", "fare_source_with_date_url": True},
                {
                    "status": fare["status"],
                    "fare_source_with_date_url": bool(fare_sources)
                    and all(
                        x.get("source_url") and x.get("verified_at")
                        for x in fare_sources
                    ),
                },
            )
        else:
            check(
                "API-13-fare-without-evidence",
                {"status": "cannot_answer", "sources": [], "has_digits": False},
                {
                    "status": fare["status"],
                    "sources": fare["sources"],
                    "has_digits": any(c.isdigit() for c in fare["assistant_message"]),
                },
            )
        invalid = Api(http).post(
            "/messages", {"message": "", "selected_poi_id": "poi-invented"}
        )
        body = invalid.json()
        check(
            "API-14-unregistered-poi",
            {"http": 200, "status": "needs_clarification", "destination": None},
            {
                "http": invalid.status_code,
                "status": body.get("status"),
                "destination": body.get("destination"),
            },
        )

    # The image supplied to /messages must reach LLMAgent.vision, not just /localizations.
    photo_llm = FakeLLM(
        scene={"image_quality": "usable", "facilities": ["ticket_machine"]}
    )
    photo_vision = LLMVision(photo_llm)
    with TestClient(
        create_app(
            agent=LLMAgent(photo_llm, search_knowledge=knowledge, vision=photo_vision),
            vision=photo_vision,
        ),
        raise_server_exceptions=False,
    ) as http:
        api = Api(http)
        api.say("직통열차")
        response = api.post(
            "/messages",
            data={"message": "이거 뭐 눌러?"},
            files={"image": ("machine.jpg", jpeg, "image/jpeg")},
        )
        body = response.json()
        check(
            "API-15-photo-question",
            {"http": 200, "status": "answered", "has_ticket_source": True},
            {
                "http": response.status_code,
                "status": body.get("status"),
                "has_ticket_source": any(
                    x["document_id"] == "doc-express-ticket"
                    for x in body.get("sources", [])
                ),
            },
        )

    # FAQ Q8: no comparison evidence means no unsupported comparison.
    with TestClient(
        create_app(
            agent=LLMAgent(FakeLLM(), search_knowledge=lambda q, lang, context: []),
            vision=vision,
        ),
        raise_server_exceptions=False,
    ) as http:
        body = Api(http).say("잘 모르겠어요")
        check(
            "API-16-comparison-without-evidence",
            {
                "status": "needs_clarification",
                "sources": [],
                "items": [],
                "has_unverified_note": True,
            },
            {
                "status": body["status"],
                "sources": body["sources"],
                "items": body["items"],
                "has_unverified_note": bool(body["unverified_notes"]),
            },
        )

        if args.knowledge == "rag":
            fare = Api(http).say("직통열차 요금 얼마야?")
            check(
                "API-19-fare-without-evidence-control",
                {"status": "cannot_answer", "sources": [], "has_digits": False},
                {
                    "status": fare["status"],
                    "sources": fare["sources"],
                    "has_digits": any(c.isdigit() for c in fare["assistant_message"]),
                },
            )

    # FAQ Q10: malformed scene output -> no_match, then explicit manual confirmation.
    with TestClient(
        create_app(agent=agent, vision=LLMVision(FakeLLM(broken=True))),
        raise_server_exceptions=False,
    ) as http:
        api = Api(http)
        api.say("직통열차")
        response = api.photo()
        body = response.json()
        check(
            "API-17-malformed-photo",
            {
                "http": 200,
                "status": "no_match",
                "candidates": [],
                "action": "recapture",
                "hint": True,
            },
            {
                "http": response.status_code,
                "status": body.get("status"),
                "candidates": body.get("candidates"),
                "action": body.get("next_action"),
                "hint": bool(body.get("retake_hint")),
            },
        )
        response = api.post(
            "/location-confirmations",
            {
                "expected_revision": body["session"]["revision"],
                "method": "manual",
                "selected_node_id": "line4-gates",
            },
        )
        confirmed = response.json()
        check(
            "API-18-manual-after-no-match",
            {"http": 200, "state": "ready_to_navigate", "node": "line4-gates"},
            {
                "http": response.status_code,
                "state": confirmed.get("session", {}).get("state"),
                "node": confirmed.get("location", {}).get("node_id"),
            },
        )

    down = FakeLLM(down=True)
    with TestClient(
        create_app(
            agent=LLMAgent(down, search_knowledge=knowledge, fallback=RuleAgent()),
            vision=LLMVision(down),
        ),
        raise_server_exceptions=False,
    ) as http:
        api = Api(http)
        response = api.say("직통열차")
        check("API-09-llm-down-fallback", "destination_set", response["status"])
        response = api.photo()
        try:
            code = response.json().get("error", {}).get("code")
        except ValueError:
            code = None
        check(
            "INT-08-vision-down",
            {"http": 503, "error_code": "AI_SERVICE_UNAVAILABLE"},
            {"http": response.status_code, "error_code": code},
        )

    # Contract regression: new intents and slots must survive actual API turns,
    # not just Agent-only contexts. Keep plan facts distinct from response slots.
    with TestClient(
        create_app(agent=agent, vision=vision), raise_server_exceptions=False
    ) as http:
        purchase = Api(http)
        first = purchase.say("공항철도 표를 구입하고 싶어요")
        check(
            "API-20-purchase-intent",
            {"status": "needs_clarification", "intent": "purchase_arex_ticket"},
            {key: first[key] for key in ("status", "intent")},
        )
        bought_at = purchase.say("직통열차")
        check(
            "API-21-purchase-followup",
            {"intent": "purchase_arex_ticket", "poi": "poi-express-tickets"},
            {
                "intent": bought_at["intent"],
                "poi": (bought_at.get("destination") or {}).get("poi_id"),
            },
        )

        exit_api = Api(http)
        exit_api.say("1번 출구로 가고 싶어요")
        exit_api.say("가지고 있어요")
        before_return = exit_api.say("아직 안 했어요")
        check(
            "API-22-exit-persisted-slots",
            {
                "intent": "navigate_to_exit",
                "exit_number": "1",
                "has_single_use_card": "yes",
                "single_use_card_returned": "no",
                "poi": "poi-single-use-card-refund",
            },
            {
                "intent": before_return["intent"],
                **{
                    key: before_return["slots"][key]
                    for key in (
                        "exit_number",
                        "has_single_use_card",
                        "single_use_card_returned",
                    )
                },
                "poi": (before_return.get("destination") or {}).get("poi_id"),
            },
        )
        returned = exit_api.say("반납했어요")
        check(
            "API-23-exit-after-return",
            {"exit_number": "1", "returned": "yes", "poi": "poi-exit-1"},
            {
                "exit_number": returned["slots"]["exit_number"],
                "returned": returned["slots"]["single_use_card_returned"],
                "poi": (returned.get("destination") or {}).get("poi_id"),
            },
        )

        board = Api(http)
        board.say("공항철도 타러 가고 싶어요")
        board.say("직통열차")
        no_ticket = board.say("아직 안 샀어요")
        check(
            "API-24-boarding-without-ticket",
            {"intent": "board_arex", "ticket": "no", "poi": "poi-express-tickets"},
            {
                "intent": no_ticket["intent"],
                "ticket": no_ticket["slots"]["has_ticket"],
                "poi": (no_ticket.get("destination") or {}).get("poi_id"),
            },
        )
        ticket_ready = board.say("구입했어요")
        check(
            "API-25-boarding-ticket-persisted",
            {"intent": "board_arex", "ticket": "yes", "poi": "poi-express-platform"},
            {
                "intent": ticket_ready["intent"],
                "ticket": ticket_ready["slots"]["has_ticket"],
                "poi": (ticket_ready.get("destination") or {}).get("poi_id"),
            },
        )

        plan_reply = http.get(
            "/api/v1/sessions/" + exit_api.sid + "/plan",
            headers={"Authorization": "Bearer " + exit_api.token},
        )
        plan_state = plan_reply.json()
        check(
            "API-26-plan-follows-reported-refund",
            {
                "http": 200,
                "refund_status": "REFUNDED",
                "unfinished_refund_steps": 0,
            },
            {
                "http": plan_reply.status_code,
                "refund_status": plan_state.get("facts", {}).get("refund_status"),
                "unfinished_refund_steps": sum(
                    step["type"] == "REFUND_SINGLE_USE_CARD"
                    and step["status"] not in ("COMPLETED", "SKIPPED")
                    for step in (plan_state.get("plan") or {}).get("steps", [])
                ),
            },
        )

    if rag_metadata is not None:
        _, final_metadata = load_rag(root, args.rag_min_score)
        if final_metadata != rag_metadata:
            raise InputError("RAG input changed during API probe; report not published")

    report = {
        "probe_version": "r6-boundary-v2",
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "commits": commits,
        "map": map_info,
        "scope": f"Real Backend API + R2 modules; FakeLLM, {args.knowledge} knowledge, synthetic JPEG; disposable DB; explicit injection, not production defaults",
        "knowledge_profile": args.knowledge,
        "rag": rag_metadata,
        "runner_sha256": digest(Path(__file__)),
        "rag_inputs_sha256": digest(Path(__file__).with_name("rag_inputs.py"))
        if rag_metadata
        else None,
        "checks": checks,
        "passed": sum(c["passed"] for c in checks),
        "total": len(checks),
        "production_ai_quality_measured": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0 if all(c["passed"] for c in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
