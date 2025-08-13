"""Bridge module mapping pipeline.classifier to src.pipeline.classifier.

Allows `from pipeline.classifier import classify` to work without src prefix.
"""
from __future__ import annotations
from src.pipeline.classifier import (  # type: ignore
    classify,
    ClassificationResult,
)
__all__ = ["classify", "ClassificationResult"]
