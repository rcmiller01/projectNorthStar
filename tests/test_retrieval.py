from bigquery_client import BigQueryClient
import retrieval


def test_retrieve_basic() -> None:
    c = BigQueryClient(project_id="demo")
    results = retrieval.retrieve(c, "test query", top_k=4)
    assert len(results) == 4
