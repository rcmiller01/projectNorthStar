"""Central environment config helper."""
from __future__ import annotations
import os

PROJECT_ID = os.getenv("PROJECT_ID", "bq_project_northstar")
DATASET = os.getenv("DATASET", "demo_ai")
LOCATION = os.getenv("LOCATION", "US")
# Model identifiers must be fully-qualified: "project.dataset.model"
EMBED_MODEL = os.getenv("BQ_EMBED_MODEL", "")
GEN_MODEL = os.getenv("BQ_GEN_MODEL", "")

__all__ = [
    "PROJECT_ID",
    "DATASET",
    "LOCATION",
    "EMBED_MODEL",
    "GEN_MODEL",
]
