"""Prevent both false alarms and missed Vision outage contract regressions."""

import pytest
from app.ai.contracts import VisionUnavailable
from audit_contracts import probe_vision_failure
from hangil_r2 import FakeLLM, LLMVision
from hangil_r2.backend.contracts import VisionUnavailable as MirrorVisionUnavailable


class FailingVision:
    def __init__(self, error):
        self.error = error

    def extract(self, image):
        raise self.error


class SwallowedFailureVision:
    def extract(self, image):
        return None


class BackendVisionSubclass(VisionUnavailable):
    pass


def test_current_agent_outage_is_caught_even_when_mirror_classes_differ():
    assert MirrorVisionUnavailable is not VisionUnavailable
    passed, evidence = probe_vision_failure(
        LLMVision(FakeLLM(down=True)), VisionUnavailable
    )
    assert passed
    assert evidence["backend_caught"]
    assert evidence["outcome"] == "expected_exception"
    assert evidence["actual_exception"] == evidence["expected_exception"]


@pytest.mark.parametrize("error_type", [MirrorVisionUnavailable, RuntimeError])
def test_wrong_exception_is_a_failed_contract_without_exposing_its_message(error_type):
    passed, evidence = probe_vision_failure(
        FailingVision(error_type("private diagnostic")), VisionUnavailable
    )
    assert not passed
    assert not evidence["backend_caught"]
    assert evidence["outcome"] == "unexpected_exception"
    assert evidence["actual_exception"] == (
        f"{error_type.__module__}.{error_type.__qualname__}"
    )
    assert "private diagnostic" not in str(evidence)


def test_swallowed_outage_does_not_pass_the_contract():
    passed, evidence = probe_vision_failure(SwallowedFailureVision(), VisionUnavailable)
    assert not passed
    assert not evidence["backend_caught"]
    assert evidence["outcome"] == "no_exception"
    assert evidence["actual_exception"] is None


def test_backend_exception_subclass_is_caught():
    passed, evidence = probe_vision_failure(
        FailingVision(BackendVisionSubclass()), VisionUnavailable
    )
    assert passed
    assert evidence["backend_caught"]
    assert evidence["outcome"] == "expected_exception"
