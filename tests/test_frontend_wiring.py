"""INT-06 must distinguish reviewed HTTP wiring, incomplete code and unknown code."""

import copy
import hashlib
import json

import pytest
from frontend_wiring import (
    FEATURES,
    classify,
    inspect_frontend,
    load_registry,
    snapshot,
)


@pytest.fixture
def reviewed(tmp_path):
    repo = tmp_path / "app"
    (repo / "src/api").mkdir(parents=True)
    (repo / "src/store.tsx").write_text(
        "if (API_MODE === 'http') sendPhoto(); else SCENARIOS[p.scenario];"
    )
    (repo / "src/api/client.ts").write_text(
        "export const sendPhoto = () => fetch('/localizations')"
    )
    files = snapshot(repo)
    profile = {
        "id": "reviewed-http",
        "reviewed_commit": "test-revision",
        "status": "wired",
        "connected_features": sorted(FEATURES),
        "missing_features": [],
        "evidence": [
            "Review fixture: HTTP handler connected; mock branch intentionally retained"
        ],
        "files_sha256": files,
    }
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"schema_version": 1, "profiles": [profile]}))
    return repo, path


def test_reviewed_http_with_mock_branch_does_not_mean_disconnected(reviewed):
    repo, path = reviewed
    result = inspect_frontend(repo, path)
    assert result["status"] == "wired"
    assert result["runtime_browser_e2e"] == "NOT_RUN"
    assert result["functional_acceptance"] == "pending_independent_runtime_checks"


def test_reviewed_old_local_flow_still_fails(reviewed):
    repo, path = reviewed
    registry = load_registry(path)
    p = registry["profiles"][0]
    p.update(
        status="incomplete",
        connected_features=["chat"],
        missing_features=sorted(FEATURES - {"chat"}),
    )
    result = classify(snapshot(repo), registry)
    assert result["status"] == "incomplete"
    assert "routes" in result["missing_features"]


def test_comments_or_unused_helpers_cannot_promote_unknown_code(reviewed):
    repo, path = reviewed
    p = repo / "src/store.tsx"
    p.write_text(
        "// sendPhoto routeOnServer deliverEvents; API_MODE === 'http'\nconst unused = () => sendPhoto()"
    )
    result = inspect_frontend(repo, path)
    assert result["status"] == "review_required"
    assert result["changed_files"] == ["src/store.tsx"]


@pytest.mark.parametrize("change", ["adapter", "dependency", "delete", "new_runtime"])
def test_changed_runtime_requires_review_even_when_store_is_unchanged(reviewed, change):
    repo, path = reviewed
    if change == "adapter":
        (repo / "src/api/client.ts").write_text("export const sendPhoto = () => null")
    elif change == "dependency":
        (repo / "package.json").write_text('{"dependencies": {"new": "1.0"}}')
    elif change == "delete":
        (repo / "src/api/client.ts").unlink()
    else:
        (repo / "src/new.ts").write_text("export const newRuntime = true")
    assert inspect_frontend(repo, path)["status"] == "review_required"


def test_doc_and_test_changes_do_not_invalidate_runtime_review(reviewed):
    repo, path = reviewed
    (repo / "README.md").write_text("documentation only")
    (repo / "src/api/client.test.ts").write_text("test-only file")
    assert inspect_frontend(repo, path)["status"] == "wired"


def test_missing_sources_are_not_silently_approved(reviewed, tmp_path):
    _, path = reviewed
    assert inspect_frontend(tmp_path / "missing", path)["status"] == "review_required"


def test_registry_cannot_approve_incomplete_flow(reviewed):
    _, path = reviewed
    data = json.loads(path.read_text())
    data["profiles"][0]["missing_features"] = ["routes"]
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="overlap"):
        load_registry(path)


def test_registry_sha_changes_with_review_evidence(reviewed):
    repo, path = reviewed
    first = inspect_frontend(repo, path)
    data = json.loads(path.read_text())
    altered = copy.deepcopy(data)
    altered["profiles"][0]["evidence"] = ["new review evidence"]
    path.write_text(json.dumps(altered))
    second = inspect_frontend(repo, path)
    assert first["registry_sha256"] != second["registry_sha256"]
    assert second["registry_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
