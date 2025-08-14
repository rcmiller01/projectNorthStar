"""Shared BigQuery helper utilities."""
from __future__ import annotations

from typing import Optional

try:  # pragma: no cover - import guard
    from google.cloud import bigquery  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "google-cloud-bigquery not installed. Install with: "
        "pip install -e .[bigquery]"
    ) from e


def model_exists(client: "bigquery.Client", fq_model_id: str) -> bool:
    """Return True if fully-qualified model id (proj.ds.name) exists."""
    if not fq_model_id or fq_model_id.count(".") != 2:
        return False
    proj, ds, name = fq_model_id.split(".")
    q = f"""
    SELECT 1
    FROM `{proj}.{ds}.INFORMATION_SCHEMA.MODELS`
    WHERE model_name = @name
    LIMIT 1
    """
    job = client.query(
        q,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("name", "STRING", name)
            ]
        ),
    )
    return job.result().total_rows > 0


def dataset_location(
    client: "bigquery.Client", project_id: str, dataset: str
) -> Optional[str]:
    """Return dataset location (e.g., 'US', 'EU', 'us-central1') or None."""
    try:
        ds = client.get_dataset(f"{project_id}.{dataset}")
        return getattr(ds, "location", None)
    except Exception:  # pragma: no cover - narrow error surface
        return None


__all__ = ["model_exists", "dataset_location"]
