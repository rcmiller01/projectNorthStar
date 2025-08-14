"""Log parsing utilities.

parse_log(path) -> normalized line records with timestamp/component extraction.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
import hashlib

# ISO / RFC3339 basic pattern (simplified)
_TS_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?"
    r"(?:Z|[+-]\d{2}:?\d{2})?)"
)
_COMPONENT_RE = re.compile(
    r"\[(?P<comp>[A-Za-z0-9_\-]+)\]|(?P<comp2>[A-Za-z0-9_]+):"
)


def _hash_file(path: Path) -> str:
    h = hashlib.sha1()
    data = path.read_bytes()
    h.update(data)
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:16] + ":" + path.name


def parse_log(path: str) -> List[Dict[str, Any]]:
    p = Path(path).resolve()
    if not p.exists():
        return []
    doc_id = _hash_file(p)
    uri = p.as_uri()
    out: List[Dict[str, Any]] = []
    for idx, line in enumerate(
        p.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
    ):
        raw = line.strip()
        if not raw:
            continue
        ts_match = _TS_RE.search(raw)
        comp_match = _COMPONENT_RE.search(raw)
        timestamp: Optional[str] = ts_match.group("ts") if ts_match else None
        component: Optional[str] = None
        if comp_match:
            component = comp_match.group("comp") or comp_match.group("comp2")
        out.append(
            {
                "doc_id": doc_id,
                "type": "log",
                "uri": uri,
                "line_no": idx,
                "text": raw,
                "meta": {
                    "filename": p.name,
                    "line_no": idx,
                    "timestamp": timestamp,
                    "component": component,
                },
            }
        )
    return out
