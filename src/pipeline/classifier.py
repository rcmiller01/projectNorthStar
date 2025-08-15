"""Rule + embedding hybrid classifier (stub).

Responsibilities:
- Accept raw request text and optional metadata.
- Produce (category, confidence, rationale) tuple.
- Fall back to rules first; escalate to embedding similarity or LLM if
    low confidence.

Contract (initial draft):
classify(text: str, metadata: dict | None) -> ClassificationResult

Edge cases to consider later:
- empty text
- very long text (truncate)
- unsupported language
Copyright (c) 2025 Team NorthStar
Licensed under the MIT License. See LICENSE file for details.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class ClassificationResult:
    category: str
    confidence: float
    rationale: str
    raw: dict[str, Any] | None = None


def classify(
    text: str, metadata: dict[str, Any] | None = None
) -> ClassificationResult:  # stub
    text_norm = text.strip()
    if not text_norm:
        return ClassificationResult(
            category="unknown",
            confidence=0.0,
            rationale="empty input",
            raw=None,
        )
    # naive keyword rule example
    lowered = text_norm.lower()
    if "billing" in lowered:
        return ClassificationResult(
            category="billing",
            confidence=0.6,
            rationale="keyword 'billing' matched",
            raw={"rule": "keyword:billing"},
        )
    return ClassificationResult(
        category="general",
        confidence=0.3,
        rationale="default fallback",
        raw={"rule": "default"},
    )
