from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import sys
import os

import streamlit as st

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Now import from the root level
from config import load_env
from google.cloud import bigquery

# Load environment
load_env()


def make_client():
    """Create BigQuery client with loaded config."""
    return bigquery.Client()


SQL_DIR = Path("sql")
VIEW_FILES = [
    "views_common_issues.sql",
    "views_by_severity.sql",
    "views_duplicates.sql",
]


def ensure_views(client) -> None:
    """Best-effort create/replace views (idempotent) - only in real BigQuery mode."""
    # Only try to create views if we're in real BigQuery mode and client supports it
    if os.getenv("BIGQUERY_REAL") != "1":
        st.info("📊 Running in stub mode - views not created. Set BIGQUERY_REAL=1 for live data.")
        return
    
    if not hasattr(client, 'run_sql_template'):
        st.warning("⚠️ Client doesn't support view creation. Run `make create-views` manually if needed.")
        return
    
    try:
        for f in VIEW_FILES:
            try:
                client.run_sql_template(f, {})
            except Exception as exc:  # pragma: no cover - non-fatal
                st.warning(f"Failed to create view {f}: {exc}")
    except Exception as e:
        st.warning(f"Views not created at startup: {e}. Run `make create-views` if you need live data.")


def mask_text(s: str) -> str:
    import re
    if not s:
        return s
    s = s[:200]  # hard cap
    patterns = [
        (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[redacted-email]"),
        (r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", "Bearer [redacted-token]"),
        (r"AKIA[0-9A-Z]{16}", "[redacted-aws-key]"),
    ]
    for pat, repl in patterns:
        s = re.sub(pat, repl, s)
    return s


def query_rows(client, sql: str) -> List[Dict]:
    try:
        return client.run_sql_template("_raw.sql", {"raw_sql": sql})
    except Exception as exc:  # pragma: no cover
        st.error(f"Query failed: {exc}")
        return []


def main():  # pragma: no cover - UI function
    st.set_page_config(page_title="NorthStar Issues Dashboard", layout="wide")
    st.title("Common Issues Dashboard (Read-only)")

    client = make_client()
    ensure_views(client)

    # Sidebar filters
    default_end = datetime.now()
    default_start = default_end - timedelta(days=30)
    st.sidebar.header("Filters")
    start_date = st.sidebar.date_input("Start", default_start.date())
    end_date = st.sidebar.date_input("End", default_end.date())
    severities = ["P0", "P1", "P2", "P3", "Unknown"]
    sel_sev = st.sidebar.multiselect("Severity", severities, default=severities)

    # Build filter predicates
    start_ts = f"TIMESTAMP('{start_date} 00:00:00 UTC')"
    end_ts = f"TIMESTAMP('{end_date} 23:59:59 UTC')"
    sev_in = ",".join(f"'" + s + "'" for s in sel_sev) or "'__none__'"

    # Get config values
    project_id = os.getenv('PROJECT_ID', 'your-project-id')
    dataset = os.getenv('DATASET', 'demo_ai')
    dataset_fq = f"{project_id}.{dataset}"

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Common Issues")
        sql_common = f"""
        SELECT fingerprint, issue_example, count, last_seen
        FROM `{dataset_fq}.view_common_issues`
        WHERE last_seen BETWEEN {start_ts} AND {end_ts}
        ORDER BY count DESC
        LIMIT 50
        """
        rows = query_rows(client, sql_common)
        for r in rows:
            r["issue_example"] = mask_text(r.get("issue_example", ""))
        st.dataframe(rows, use_container_width=True, hide_index=True)
        if len(rows) == 50:
            st.caption("Showing top 50 (truncated).")

    with col2:
        st.subheader("Severity Trends (Weekly)")
        sql_sev = f"""
        SELECT week, severity, count FROM `{dataset_fq}.view_issues_by_severity`
        WHERE week BETWEEN DATE({start_ts}) AND DATE({end_ts})
          AND severity IN ({sev_in})
        ORDER BY week, severity
        """
        sev_rows = query_rows(client, sql_sev)
        if sev_rows:
            import pandas as pd
            df = pd.DataFrame(sev_rows)
            pivot = df.pivot_table(index="week", columns="severity", values="count", fill_value=0)
            st.area_chart(pivot)
        else:
            st.info("No data for selected window.")

    st.subheader("Potential Duplicate Clusters")
    sql_dup = f"""
    WITH sz AS (
      SELECT group_id, COUNT(DISTINCT member_chunk_id) AS size
      FROM `{dataset_fq}.view_duplicate_chunks`
      GROUP BY group_id
    )
    SELECT d.group_id, d.member_chunk_id, d.distance, sz.size
    FROM `{dataset_fq}.view_duplicate_chunks` d
    JOIN sz USING (group_id)
    ORDER BY sz.size DESC, d.group_id
    LIMIT 200
    """
    dup_rows = query_rows(client, sql_dup)[:50]
    from collections import defaultdict
    groups: Dict[str, List[Dict]] = defaultdict(list)
    for r in dup_rows:
        groups[r["group_id"]].append(r)
    for gid, members in list(groups.items())[:50]:
        with st.expander(f"Group {gid} (size={members[0]['size']})"):
            member_ids = ",".join(f"'" + m['member_chunk_id'] + "'" for m in members[:10])
            sql_texts = f"""
            SELECT chunk_id, SUBSTR(text,1,200) AS text
            FROM `{dataset_fq}.chunks`
            WHERE chunk_id IN ({member_ids})
            """
            texts = {r['chunk_id']: mask_text(r.get('text','')) for r in query_rows(client, sql_texts)}
            for m in members:
                st.write({
                    "chunk_id": m["member_chunk_id"],
                    "distance": m["distance"],
                    "text": texts.get(m["member_chunk_id"], "")
                })
    if len(groups) == 50:
        st.caption("Showing first 50 groups (truncated).")

    st.caption("All data read-only; no writes performed.")


if __name__ == "__main__":  # pragma: no cover
    main()
