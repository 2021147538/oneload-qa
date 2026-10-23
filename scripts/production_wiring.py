"""Inspect the actual Backend entrypoint in both key branches with FakeLLM only."""

import os
import runpy
from pathlib import Path
from unittest.mock import patch

from qa_inputs import digest


def probe_entrypoint(path: Path) -> dict:
    from hangil_r2 import FakeLLM

    branches = {}
    for label, key in (("missing_key", ""), ("key_present", "r6-fake-key")):
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": key, "RAG_BACKEND": "memory"}),
            patch("hangil_r2.OpenAILLM", FakeLLM),
        ):
            namespace = runpy.run_path(str(path))
        app = namespace["app"]
        agent, vision = app.state.agent, app.state.vision
        branches[label] = {
            "agent": type(agent).__name__,
            "vision": type(vision).__name__,
            "same_vision": getattr(agent, "vision", None) is vision,
            "same_llm": getattr(agent, "llm", None) is not None
            and getattr(agent, "llm", None) is getattr(vision, "llm", None),
            "llm": type(getattr(agent, "llm", None)).__name__,
            "knowledge": type(getattr(agent, "search_knowledge", None)).__name__,
            "fallback": type(getattr(agent, "fallback", None)).__name__,
        }
    live = branches["key_present"]
    return {
        "method": "execute_actual_entrypoint_with_OpenAILLM_replaced_by_FakeLLM",
        "entrypoint_sha256": digest(path),
        "branches": branches,
        "agent_vision_conditionally_wired": live["agent"] == "LLMAgent"
        and live["vision"] == "LLMVision"
        and live["same_vision"]
        and live["same_llm"]
        and live["llm"] == "FakeLLM",
        "production_knowledge_is_demo": live["knowledge"] == "MockKnowledgeSearch",
        "real_model_calls": 0,
        "deployed_runtime_verified": False,
    }
