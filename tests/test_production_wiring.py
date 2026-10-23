"""A factory definition alone must not pass entrypoint wiring or hide demo search."""

import os
from pathlib import Path

from production_wiring import probe_entrypoint


def test_current_entrypoint_selects_shared_fake_agent_and_keeps_demo_search():
    root = Path(os.environ.get("QA_PROJECT_ROOT", Path(__file__).resolve().parents[2]))
    result = probe_entrypoint(root / "oneload-backend/app/main.py")
    assert result["agent_vision_conditionally_wired"]
    assert result["production_knowledge_is_demo"]
    assert result["branches"]["missing_key"]["agent"] == "RuleAgent"
    assert result["branches"]["missing_key"]["vision"] == "NoVision"
    assert result["branches"]["key_present"]["llm"] == "FakeLLM"
    assert result["real_model_calls"] == 0


def test_unused_factory_does_not_approve_the_actual_entrypoint(tmp_path):
    path = tmp_path / "main.py"
    path.write_text("""
from types import SimpleNamespace
from hangil_r2 import LLMAgent, LLMVision, OpenAILLM, MockKnowledgeSearch
from app.ai.rule_agent import RuleAgent
from app.ai.vision import NoVision
def production_ai():
    llm = OpenAILLM()
    vision = LLMVision(llm)
    return LLMAgent(llm, search_knowledge=MockKnowledgeSearch(), vision=vision), vision
app = SimpleNamespace(state=SimpleNamespace(agent=RuleAgent(), vision=NoVision()))
""")
    result = probe_entrypoint(path)
    assert not result["agent_vision_conditionally_wired"]


def test_separate_vision_clients_do_not_pass_shared_wiring(tmp_path):
    path = tmp_path / "main.py"
    path.write_text("""
from types import SimpleNamespace
from hangil_r2 import LLMAgent, LLMVision, OpenAILLM, MockKnowledgeSearch
agent = LLMAgent(OpenAILLM(), search_knowledge=MockKnowledgeSearch(), vision=LLMVision(OpenAILLM()))
app = SimpleNamespace(state=SimpleNamespace(agent=agent, vision=LLMVision(OpenAILLM())))
""")
    result = probe_entrypoint(path)
    assert not result["agent_vision_conditionally_wired"]
