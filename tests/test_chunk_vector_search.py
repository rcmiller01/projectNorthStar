from src.bq.bigquery_client import make_client
from src.retrieval.hybrid import chunk_vector_search


def test_chunk_vector_search_stub():
    c = make_client()
    rows = chunk_vector_search(c, "example query", k=3)
    assert rows and rows[0]["text"].startswith("chunk snippet")
    # test type filter effect
    rows2 = chunk_vector_search(c, "example query", k=3, types=["log"])
    assert rows2[0]["source"].startswith("bq.vector_search:log")
