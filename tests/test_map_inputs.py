"""Prevent obsolete fixture fallback and silent empty-map runs after repo separation."""

import json

import pytest
from app.domain.mapdata import MapData
from qa_inputs import InputError, inspect_data, load_live_map


def write_map(directory, data):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "seoul-station.json").write_text(json.dumps(data))
    return directory


def test_missing_data_repo_never_falls_back_to_backend_fixture(tmp_path, seoul_json):
    write_map(tmp_path / "oneload-backend/tests/fixtures/maps", seoul_json)
    with pytest.raises(InputError, match="Clone oneload-data"):
        load_live_map(tmp_path)


def test_missing_selected_map_fails_before_agent_invocation(tmp_path):
    (tmp_path / "oneload-data/maps").mkdir(parents=True)
    with pytest.raises(InputError, match="Selected map file is missing"):
        load_live_map(tmp_path)


def test_explicit_override_uses_selected_version_without_leaking_absolute_path(
    tmp_path, seoul_json
):
    write_map(tmp_path / "oneload-data/maps", seoul_json)
    selected = dict(seoul_json, version="override-only")
    override = write_map(tmp_path / "alternative/maps", selected)
    map_, info = load_live_map(tmp_path, override)
    assert map_.version == info["version"] == "override-only"
    assert info["source_repository"] == "override"
    assert str(tmp_path) not in json.dumps(info)


def test_empty_map_directory_is_not_a_successful_validation(tmp_path):
    (tmp_path / "oneload-data/maps").mkdir(parents=True)
    with pytest.raises(InputError, match="no JSON maps"):
        inspect_data(tmp_path)


def test_schema_drift_is_a_failed_check(tmp_path, seoul_json):
    data = dict(seoul_json, panoramas=[])
    write_map(tmp_path / "oneload-data/maps", data)
    schema = tmp_path / "oneload-data/schema"
    schema.mkdir()
    (schema / "map.schema.json").write_text("{}")
    report = inspect_data(tmp_path)
    assert not next(c for c in report["checks"] if c["id"] == "DATA-schema")["passed"]


def test_missing_photo_is_reported_with_panorama_ids(tmp_path, seoul_json):
    write_map(tmp_path / "oneload-data/maps", seoul_json)
    schema = tmp_path / "oneload-data/schema"
    schema.mkdir()
    (schema / "map.schema.json").write_text(json.dumps(MapData.model_json_schema()))
    report = inspect_data(tmp_path)
    photos = next(c for c in report["checks"] if c["id"] == "DATA-photos-seoul-station")
    assert not photos["passed"]
    assert set(photos["missing_panorama_ids"]) == {
        p["pano_id"] for p in seoul_json["panoramas"]
    }
