"""Shared live-map resolution and version evidence for all QA entry points."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

SOURCE_REPOS = (
    "oneload-app",
    "oneload-backend",
    "oneload_agent",
    "oneload-data",
    "oneload-infra",
)


class InputError(ValueError):
    """A missing or invalid QA input, reported before model or DB calls."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_commits(root: Path) -> dict[str, str]:
    commits = {}
    for name in SOURCE_REPOS:
        try:
            commits[name] = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=root / name,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise InputError(
                "Expected a Git checkout for sibling repository: " + name
            ) from exc
    return commits


def resolve_map_dir(root: Path, override: Path | None = None) -> Path:
    directory = (
        override if override is not None else root / "oneload-data/maps"
    ).resolve()
    if not directory.is_dir():
        raise InputError(
            "Map directory not found. Clone oneload-data beside oneload-backend, or pass --map-dir."
        )
    return directory


def load_live_map(
    root: Path, override: Path | None = None, map_id: str = "seoul-station"
):
    from app.domain.mapdata import MapData

    directory = resolve_map_dir(root, override)
    path = directory / (map_id + ".json")
    if not path.is_file():
        raise InputError("Selected map file is missing: " + path.name)
    try:
        map_ = MapData.model_validate_json(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise InputError(
            "Selected map failed Backend MapData validation: " + path.name
        ) from exc
    if map_.map_id != map_id:
        raise InputError("Map file name and map_id do not match: " + path.name)
    canonical = (root / "oneload-data").resolve()
    source = "oneload-data" if path.is_relative_to(canonical) else "override"
    label = str(path.relative_to(canonical)) if source == "oneload-data" else path.name
    return map_, {
        "source_repository": source,
        "path": label,
        "map_id": map_.map_id,
        "version": map_.version,
        "sha256": digest(path),
    }


def inspect_data(root: Path, override: Path | None = None) -> dict:
    """Validate live maps with Backend models, schema copy, and on-disk photo references."""
    from app.domain.mapdata import MapData

    directory = resolve_map_dir(root, override)
    data_root = directory.parent
    paths = sorted(directory.glob("*.json"))
    if not paths:
        raise InputError("Selected map directory contains no JSON maps.")
    checks, records, assets = [], [], {}
    schema = data_root / "schema/map.schema.json"
    schema_matches = (
        schema.is_file()
        and json.loads(schema.read_text()) == MapData.model_json_schema()
    )
    checks.append(
        {
            "id": "DATA-schema",
            "passed": schema_matches,
            "description": "Data schema equals the current Backend MapData schema",
        }
    )
    for path in paths:
        try:
            map_, metadata = load_live_map(root, directory, path.stem)
            checks.append(
                {
                    "id": "DATA-map-" + path.stem,
                    "passed": True,
                    "description": "Backend schema and cross-reference validation",
                }
            )
        except InputError as exc:
            checks.append(
                {
                    "id": "DATA-map-" + path.stem,
                    "passed": False,
                    "description": str(exc),
                }
            )
            continue
        missing = []
        for pano in map_.panoramas:
            photo = (data_root / pano.image_url.lstrip("/")).resolve()
            # Do not read an arbitrary file outside the selected data tree.
            if not photo.is_relative_to(data_root.resolve()) or not photo.is_file():
                missing.append(pano.pano_id)
            else:
                assets[str(photo.relative_to(data_root.resolve()))] = digest(photo)
        checks.append(
            {
                "id": "DATA-photos-" + path.stem,
                "passed": not missing,
                "missing_panorama_ids": missing,
            }
        )
        records.append(
            {
                **metadata,
                "nodes": len(map_.nodes),
                "edges": len(map_.edges),
                "pois": len(map_.pois),
                "panoramas": len(map_.panoramas),
                "example_panoramas": sum(p.is_example for p in map_.panoramas),
            }
        )
    return {
        "checks": checks,
        "maps": records,
        "asset_sha256": assets,
        "passed": sum(c["passed"] for c in checks),
        "total": len(checks),
        "validation_scope": "Backend MapData and reference validation; schema copy equality; local photo files",
        "field_photo_accuracy_measured": False,
    }
