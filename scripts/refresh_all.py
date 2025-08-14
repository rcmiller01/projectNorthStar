"""Full embedding refresh batching helper.

Runs refresh_embeddings(loop=True) using the real client if BIGQUERY_REAL=1.
Falls back to stub (no-op) otherwise.
"""
from __future__ import annotations
from bq import make_client
from bq.refresh import refresh_embeddings


def main() -> None:  # pragma: no cover
    client = make_client()
    result = refresh_embeddings(client, loop=True)
    print(result)


if __name__ == "__main__":  # pragma: no cover
    main()
