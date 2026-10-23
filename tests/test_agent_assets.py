"""Asset evidence must follow the imported Agent rather than stale root copies."""

import pytest
from evaluate_agent import agent_assets
from qa_inputs import InputError


def assets(root):
    prompts, mocks = root / "prompts", root / "mocks"
    prompts.mkdir(parents=True)
    mocks.mkdir(parents=True)
    for name in ("understand", "compose", "scene"):
        (prompts / f"{name}_v3.md").write_text(name)
    (mocks / "knowledge.json").write_text("{}")
    return prompts, mocks


@pytest.mark.parametrize("packaged", [False, True])
def test_actual_assets_are_recorded(tmp_path, packaged):
    root = tmp_path / "hangil_r2" if packaged else tmp_path
    prompts, mocks = assets(root)
    if packaged:
        assets(tmp_path)  # Obsolete copies must not enter the evidence.
    p, m = agent_assets(tmp_path, "v3", prompts, mocks)
    assert all(path.parent == prompts for path in p)
    assert m == [mocks / "knowledge.json"]


def test_missing_imported_assets_do_not_fall_back(tmp_path):
    assets(tmp_path)
    with pytest.raises(InputError, match="prompt version"):
        agent_assets(tmp_path, "v3", tmp_path / "hangil_r2/prompts", tmp_path / "mocks")


def test_assets_from_another_checkout_rejected(tmp_path):
    prompts, mocks = assets(tmp_path / "other")
    with pytest.raises(InputError, match="selected checkout"):
        agent_assets(tmp_path / "selected", "v3", prompts, mocks)
