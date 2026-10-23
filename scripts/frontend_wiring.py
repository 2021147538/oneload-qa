"""Audit reviewed Frontend call paths without inferring execution from text markers.

A registry entry records a human/agent source review, not a browser test. Unknown
runtime source must be reviewed before it can inherit a previous wiring verdict.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from qa_inputs import digest

DEPENDENCY_FILES = ("package.json", "pnpm-lock.yaml", "vite.config.ts")
FEATURES = {"chat", "localization", "confirmation", "routes", "navigation_events"}


def runtime_paths(paths):
    return sorted(
        p
        for p in paths
        if p in DEPENDENCY_FILES
        or (
            p.startswith("src/")
            and p.endswith((".ts", ".tsx"))
            and not p.startswith("src/test/")
            and not p.endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx"))
        )
    )


def snapshot(repo: Path):
    paths = runtime_paths(
        [
            *(
                str(p.relative_to(repo))
                for p in (repo / "src").rglob("*")
                if p.is_file()
            ),
            *(p for p in DEPENDENCY_FILES if (repo / p).is_file()),
        ]
    )
    return {path: digest(repo / path) for path in paths}


def load_registry(path: Path):
    data = json.loads(path.read_text())
    if data.get("schema_version") != 1 or not data.get("profiles"):
        raise ValueError("Frontend review registry is missing or unsupported")
    seen = set()
    for p in data["profiles"]:
        if p["id"] in seen or p["status"] not in {"wired", "incomplete"}:
            raise ValueError("Invalid or duplicate Frontend review profile")
        seen.add(p["id"])
        if (
            not p.get("reviewed_commit")
            or not p.get("evidence")
            or not p.get("files_sha256")
        ):
            raise ValueError(
                "Review profile requires a commit, evidence and source hashes"
            )
        if (
            set(p.get("connected_features", [])) | set(p.get("missing_features", []))
            != FEATURES
        ):
            raise ValueError("Review must account for all required HTTP flows")
        if set(p.get("connected_features", [])) & set(p.get("missing_features", [])):
            raise ValueError("Connected and missing features overlap")
        if (p["status"] == "wired") != (not p.get("missing_features")):
            raise ValueError("Incomplete HTTP flows cannot be approved as wired")
        for name, sha in p["files_sha256"].items():
            if (
                name not in runtime_paths([name])
                or len(sha) != 64
                or any(c not in "0123456789abcdef" for c in sha)
            ):
                raise ValueError("Invalid runtime source path or SHA256")
    return data


def classify(files, registry):
    common = {
        "method": "reviewed_runtime_source_fingerprints",
        "runtime_browser_e2e": "NOT_RUN",
        "functional_acceptance": "pending_independent_runtime_checks",
        "snapshot_sha256": hashlib.sha256(
            json.dumps(files, sort_keys=True).encode()
        ).hexdigest(),
    }
    for profile in registry["profiles"]:
        if profile["files_sha256"] == files:
            return {
                **common,
                "status": profile["status"],
                "profile": profile["id"],
                "reviewed_commit": profile["reviewed_commit"],
                "connected_features": profile["connected_features"],
                "missing_features": profile["missing_features"],
                "evidence": profile["evidence"],
            }
    nearest = min(
        registry["profiles"], key=lambda p: len(changed_paths(files, p["files_sha256"]))
    )
    return {
        **common,
        "status": "review_required",
        "nearest_profile": nearest["id"],
        "changed_files": changed_paths(files, nearest["files_sha256"]),
        "reason": "Runtime code/dependencies differ from reviewed call paths; do not assume connected or disconnected",
    }


def changed_paths(left, right):
    return sorted(k for k in left.keys() | right.keys() if left.get(k) != right.get(k))


def inspect_frontend(repo: Path, registry_path: Path):
    registry = load_registry(registry_path)
    result = classify(snapshot(repo), registry)
    result["registry_sha256"] = digest(registry_path)
    return result
