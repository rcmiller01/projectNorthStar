"""Chunking utilities for OCR/log records.

Approximate tokens by word count (1 word ~1 token). Provides overlap.
Hard caps max_tokens to 4096 to avoid pathological giant chunks.
"""
from __future__ import annotations
from typing import List, Dict, Any
import hashlib


def _approx_tokens(words: int) -> int:
    # Placeholder heuristic (1 word ~1 token for now)
    return words


def _hash(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()


def to_chunks(
    records: List[Dict[str, Any]], max_tokens: int = 512, overlap: int = 50
) -> List[Dict[str, Any]]:
    if max_tokens > 4096:  # guardrail
        max_tokens = 4096
    chunks: List[Dict[str, Any]] = []
    for r in records:
        text: str = r.get("text", "")
        if not text:
            continue
        words = text.split()
        if not words:
            continue
        window: List[str] = []
        start = 0
        i = 0
        while i < len(words):
            window.append(words[i])
            if (
                _approx_tokens(len(window)) >= max_tokens
                or i == len(words) - 1
            ):
                chunk_text = " ".join(window)
                prov_parts = []
                if "page" in r:
                    prov_parts.append(f"p{r['page']}")
                if "line_no" in r:
                    prov_parts.append(f"l{r['line_no']}")
                base = f"{r['doc_id']}:{start}:{i}:{'|'.join(prov_parts)}"
                chunk_id = _hash(base)[:24]
                meta = dict(r.get("meta") or {})
                meta.update({
                    "type": r.get("type"),
                    "uri": r.get("uri"),
                })
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "doc_id": r["doc_id"],
                        "text": chunk_text,
                        "meta": meta,
                    }
                )
                # slide window with overlap
                if overlap > 0 and len(window) > overlap:
                    window = window[-overlap:]
                    start = i - overlap + 1
                else:
                    window = []
                    start = i + 1
            i += 1
    return chunks
