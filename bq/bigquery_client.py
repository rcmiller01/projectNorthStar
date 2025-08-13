"""Shim module to allow `from bq.bigquery_client import BigQueryClientBase`.

Re-exports the implementation living under src.bq.bigquery_client.
"""
from __future__ import annotations
from src.bq.bigquery_client import *  # type: ignore  # noqa: F401,F403
