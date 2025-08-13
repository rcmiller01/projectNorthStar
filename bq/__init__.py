"""Top-level bq package exposing BigQuery client base & factory."""
from src.bq.bigquery_client import (  # noqa: F401
	BigQueryClientBase,
	make_client,
)
