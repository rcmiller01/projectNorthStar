"""BigQuery client wrapper (stub + real) for Phase 1.

Environment switch: set BIGQUERY_REAL=1 to use RealClient, else StubClient.
"""
from __future__ import annotations
from dataclasses import dataclass
import importlib
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path for config import  
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import config module for authentication handling
from config import load_env

SQL_DIR = Path("sql")


class BigQueryClientBase:
    """Interface for BigQuery client variants."""

    def run_sql_template(
        self, name: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:  # pragma: no cover - interface
        raise NotImplementedError


@dataclass
class StubClient(BigQueryClientBase):
    """Offline stub returning deterministic rows for development."""

    def run_sql_template(
        self, name: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        # Support inline raw SQL passthrough with sample data for dashboard
        if "raw_sql" in params:
            sql = params["raw_sql"].lower()
            
            # Sample data for common issues view
            if "view_common_issues" in sql:
                return [
                    {
                        "issue_fingerprint": "auth_timeout_error", 
                        "count": 15,
                        "issue_example": "Authentication service timeout after 30 seconds",
                        "last_seen": "2025-08-15 10:30:00"
                    },
                    {
                        "issue_fingerprint": "database_connection_pool", 
                        "count": 8,
                        "issue_example": "Database connection pool exhausted",
                        "last_seen": "2025-08-15 09:15:00"
                    },
                    {
                        "issue_fingerprint": "ssl_cert_expiring", 
                        "count": 3,
                        "issue_example": "SSL certificate expires in 2 days",
                        "last_seen": "2025-08-14 16:45:00"
                    }
                ]
            
            # Sample data for severity trends view 
            elif "view_issues_by_severity" in sql:
                return [
                    {"week": "2025-08-05T00:00:00Z", "severity": "P0", "count": 2},
                    {"week": "2025-08-05T00:00:00Z", "severity": "P1", "count": 5},
                    {"week": "2025-08-05T00:00:00Z", "severity": "P2", "count": 8},
                    {"week": "2025-08-05T00:00:00Z", "severity": "P3", "count": 12},
                    {"week": "2025-08-12T00:00:00Z", "severity": "P0", "count": 1},
                    {"week": "2025-08-12T00:00:00Z", "severity": "P1", "count": 3},
                    {"week": "2025-08-12T00:00:00Z", "severity": "P2", "count": 6},
                    {"week": "2025-08-12T00:00:00Z", "severity": "P3", "count": 8}
                ]
            
            # Sample data for duplicate chunks view
            elif "view_duplicate_chunks" in sql:
                return [
                    {
                        "group_id": "grp_001", 
                        "member_chunk_id": "chunk_1",
                        "distance": 0.05,
                        "size": 3
                    },
                    {
                        "group_id": "grp_001", 
                        "member_chunk_id": "chunk_2",
                        "distance": 0.08,
                        "size": 3
                    },
                    {
                        "group_id": "grp_001", 
                        "member_chunk_id": "chunk_3",
                        "distance": 0.12,
                        "size": 3
                    },
                    {
                        "group_id": "grp_002", 
                        "member_chunk_id": "chunk_4",
                        "distance": 0.03,
                        "size": 2
                    },
                    {
                        "group_id": "grp_002", 
                        "member_chunk_id": "chunk_5",
                        "distance": 0.07,
                        "size": 2
                    }
                ]
            
            # Sample data for chunk text queries
            elif "chunks" in sql and "chunk_id in" in sql:
                return [
                    {"chunk_id": "chunk_1", "text": "Database timeout error occurred during user authentication"},
                    {"chunk_id": "chunk_2", "text": "Database connection timed out after 30 seconds"},
                    {"chunk_id": "chunk_3", "text": "DB timeout during query execution"},
                    {"chunk_id": "chunk_4", "text": "Authentication failed for user login"},
                    {"chunk_id": "chunk_5", "text": "Auth service rejected login request"}
                ]
            
            # Default empty for other raw SQL queries
            return []
            
        if name == "vector_search.sql":
            q = params.get("query_text", "")
            return [
                {"id": 1, "text": f"stub snippet for: {q}", "distance": 0.05},
            ]
        if name == "chunk_vector_search.sql":
            q = params.get("query_text", "")
            types = params.get("types") or []
            base = {
                "chunk_id": "chunk_1",
                "text": f"chunk snippet for: {q}",
                "distance": 0.07,
                "meta": {
                    "type": (types[0] if types else "pdf"),
                    "filename": "stub.pdf",
                },
            }
            return [base]
        return []


@dataclass
class RealClient(BigQueryClientBase):
    """Real BigQuery client using google-cloud-bigquery (best-effort)."""

    project: str | None = None
    location: str | None = None

    def __post_init__(self) -> None:
        try:  # lazy import
            bigquery_mod = importlib.import_module("google.cloud.bigquery")
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "bigquery lib missing; install or unset BIGQUERY_REAL."
            ) from exc
        self._bq_mod = bigquery_mod
        
        # Support different authentication methods
        api_key = os.getenv("GOOGLE_API_KEY")
        service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if api_key:
            # Use API key authentication (for testing)
            from google.auth.credentials import AnonymousCredentials
            self._client = bigquery_mod.Client(
                project=self.project,
                location=self.location,
                credentials=AnonymousCredentials()
            )
            # Note: API keys have limited BigQuery support
            print(f"[auth] Using API key authentication for project "
                  f"{self.project}")
        elif service_account_path:
            # Use service account file
            self._client = bigquery_mod.Client(
                project=self.project, location=self.location
            )
            print(f"[auth] Using service account from {service_account_path}")
        else:
            # Use default credentials (ADC)
            self._client = bigquery_mod.Client(
                project=self.project, location=self.location
            )
            print(f"[auth] Using default credentials for project "
                  f"{self.project}")

    def run_sql_template(
        self, name: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        # Raw SQL bypass
        if "raw_sql" in params:
            sql = params["raw_sql"]
        else:
            path = SQL_DIR / name
            if not path.exists():  # pragma: no cover
                raise FileNotFoundError(f"SQL template not found: {name}")
            sql_src = path.read_text(encoding="utf-8")
            sql = sql_src
        # Parameter placeholders
        batch_limit_env = os.getenv("EMBED_BATCH_LIMIT", "10000")
        try:
            batch_limit = min(50000, max(1, int(batch_limit_env)))
        except ValueError:
            batch_limit = 10000
        replacements = {
            "${PROJECT_ID}": self.project or "",
            "${DATASET}": os.getenv("BQ_DATASET", "demo_ai"),
            "${EMBED_MODEL}": os.getenv(
                "BQ_EMBED_MODEL", "text-embedding-004"
            ),
            "${QUERY_TEXT}": f"'{params.get('query_text', '')}'",
            "${TOP_K}": str(params.get("top_k", 5)),
            "${EMBED_BATCH_LIMIT}": str(batch_limit),
            "${TYPE_ARRAY}": (
                "[" + ",".join(f"'{t}'" for t in params.get("types", [])) + "]"
                if params.get("types")
                else "[]"
            ),
        }
        for k, v in replacements.items():
            sql = sql.replace(k, v)
        try:
            job = self._client.query(sql)
            rows = list(job.result())
        except Exception as exc:  # pragma: no cover
            if "credentials" in str(exc).lower():
                raise RuntimeError(
                    "BigQuery creds missing; set env or unset BIGQUERY_REAL."
                ) from exc
            raise
        out: List[Dict[str, Any]] = []
        for r in rows:
            d = dict(r)
            out.append(d)
        return out


def make_client() -> BigQueryClientBase:
    """Factory for appropriate client based on env switch."""
    if os.getenv("BIGQUERY_REAL") == "1":
        return RealClient(
            project=os.getenv("BQ_PROJECT_ID"),
            location=os.getenv("BQ_LOCATION"),
        )
    return StubClient()

# Reflection:
# Created stub + real client with simple template substitution.
# Next improvement: parameter binding and query caching.
