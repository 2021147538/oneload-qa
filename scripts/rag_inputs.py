"""Explicit local MemorySearch profile; never follows RAG_BACKEND or calls a model."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from qa_inputs import InputError, digest


def load_rag(root: Path, min_score: float = 0.25):
    repo = root / "oneload-rag"
    required = [repo / "src/hangil_rag/search_memory.py", repo / "knowledge/README.md"]
    if not all(p.is_file() for p in required) or not (repo / ".git").exists():
        raise InputError(
            "RAG profile requires sibling oneload-rag checkout and knowledge"
        )
    if not 0 <= min_score <= 1:
        raise InputError("RAG min_score must be between 0 and 1")
    # Use this checkout rather than an installed wheel or env-selected pgvector.
    src = (repo / "src").resolve()
    sys.path.insert(0, str(src))
    from hangil_rag import search_memory
    from hangil_rag.loader import load_docs

    if not Path(search_memory.__file__).resolve().is_relative_to(src):
        raise InputError(
            "Another hangil_rag package is already loaded; use a fresh process"
        )
    docs = load_docs(repo / "knowledge", include_community=False)
    if not docs or any(d.source_kind != "official" for d in docs):
        raise InputError("QA RAG profile requires official knowledge documents only")
    search = search_memory.MemorySearch(docs=docs, k=3, min_score=min_score)
    metadata = {
        "repository": "oneload-rag",
        "commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo, text=True
        ).strip(),
        "working_tree_clean": not bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=repo, text=True
            ).strip()
        ),
        "backend": "MemorySearch",
        "min_score": min_score,
        "k": 3,
        "relative_cutoff": search_memory.RELATIVE_CUTOFF,
        "scope_gate_min_coverage": getattr(search_memory, "MIN_COVERAGE", None),
        "community": False,
        "document_ids": sorted(d.doc_id for d in docs),
        "knowledge_sha256": {
            p.name: digest(p) for p in sorted((repo / "knowledge").glob("*.md"))
        },
        "code_sha256": {
            str(p.relative_to(repo)): digest(p)
            for p in sorted((repo / "src/hangil_rag").glob("*.py"))
        },
        "live_model_calls": 0,
        "live_embedding_calls": 0,
    }
    return search, metadata
