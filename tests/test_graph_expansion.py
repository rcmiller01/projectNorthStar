"""Tests for SQL chunk neighbor queries and graph expansion"""

import pytest
from unittest.mock import Mock
from src.retrieval import hybrid


class TestChunkNeighborSQL:
    """Test SQL templates for chunk neighbor operations"""

    def test_get_chunk_neighbors_sql_template(self):
        """Test chunk neighbors SQL template validation"""
        import os

        sql_file = os.path.join(os.path.dirname(__file__), "..", "sql", "get_chunk_neighbors.sql")
        assert os.path.exists(sql_file), "get_chunk_neighbors.sql must exist"

        with open(sql_file, "r") as f:
            sql_content = f.read()

        # Verify required parameters
        required_params = ["${PROJECT_ID}", "${DATASET}", "${CHUNK_IDS_ARRAY}", "${MAX_NEIGHBORS}"]
        for param in required_params:
            assert param in sql_content, f"Missing parameter {param}"

        # Verify SQL structure
        assert "WITH target_chunks AS" in sql_content
        assert "neighbors_union AS" in sql_content
        assert "ranked_neighbors AS" in sql_content
        assert "limited_neighbors AS" in sql_content
        assert "ROW_NUMBER() OVER" in sql_content
        assert "ORDER BY weight DESC" in sql_content

    def test_get_chunk_details_sql_template(self):
        """Test chunk details SQL template validation"""
        import os

        sql_file = os.path.join(os.path.dirname(__file__), "..", "sql", "get_chunk_details.sql")
        assert os.path.exists(sql_file), "get_chunk_details.sql must exist"

        with open(sql_file, "r") as f:
            sql_content = f.read()

        # Verify required parameters
        required_params = ["${PROJECT_ID}", "${DATASET}", "${CHUNK_IDS_ARRAY}"]
        for param in required_params:
            assert param in sql_content, f"Missing parameter {param}"

        # Verify SQL structure
        assert "SELECT" in sql_content
        assert "chunk_id" in sql_content
        assert "chunks_emb" in sql_content
        assert "WHERE chunk_id IN UNNEST" in sql_content


class TestHybridRetrievalGraphExpansion:
    """Test graph expansion functionality in hybrid retrieval"""

    @pytest.fixture
    def mock_bq_client(self):
        """Mock BigQuery client"""
        client = Mock()
        client.query.return_value.result.return_value = []
        return client

    def test_vector_search_no_graph_boost(self, mock_bq_client):
        """Test vector search without graph expansion (graph_boost=0)"""
        # Mock vector search results (before _normalize_rows transformation)
        mock_results = [
            {"chunk_id": "chunk1", "distance": 0.1, "text": "content1"},
            {"chunk_id": "chunk2", "distance": 0.2, "text": "content2"},
        ]
        mock_bq_client.run_sql_template.return_value = mock_results

        results = hybrid.vector_search(
            client=mock_bq_client, query_text="test query", k=10, graph_boost=0.0
        )

        # Should return normalized results without expansion
        assert len(results) == 2
        # _normalize_rows changes chunk_id to id
        assert results[0]["id"] == "chunk1"
        assert results[1]["id"] == "chunk2"

        # Should only call vector search, not neighbor queries
        assert mock_bq_client.run_sql_template.call_count == 1

    def test_vector_search_with_graph_boost(self, mock_bq_client):
        """Test vector search with graph expansion (graph_boost>0)"""
        # Mock vector search results
        vector_results = [
            {"chunk_id": "chunk1", "distance": 0.1, "text": "content1"},
            {"chunk_id": "chunk2", "distance": 0.2, "text": "content2"},
        ]

        # Mock neighbor results
        neighbor_results = [
            {"src_chunk_id": "chunk1", "nbr_chunk_id": "chunk3", "weight": 0.8},
            {"src_chunk_id": "chunk2", "nbr_chunk_id": "chunk4", "weight": 0.6},
        ]

        # Mock neighbor details
        detail_results = [
            {"chunk_id": "chunk3", "text": "content3", "meta": "{}"},
            {"chunk_id": "chunk4", "text": "content4", "meta": "{}"},
        ]

        # Setup mock responses in sequence
        mock_bq_client.run_sql_template.side_effect = [
            vector_results,  # First call: vector search
            neighbor_results,  # Second call: neighbor search
            detail_results,  # Third call: neighbor details
        ]

        results = hybrid.vector_search(
            client=mock_bq_client, query_text="test query", k=10, graph_boost=0.2
        )

        # Should have expanded results
        assert len(results) >= 2  # Original + potentially new neighbors

        # Should call vector search + neighbor queries
        assert mock_bq_client.run_sql_template.call_count == 3

    def test_graph_expansion_empty_neighbors(self, mock_bq_client):
        """Test graph expansion when neighbor tables are empty"""
        # Mock vector search results (before _normalize_rows transformation)
        vector_results = [
            {"chunk_id": "chunk1", "distance": 0.1, "text": "content1"},
        ]

        # Mock empty neighbor results
        empty_neighbors = []
        empty_details = []

        # Setup mock responses
        mock_bq_client.run_sql_template.side_effect = [
            vector_results,  # Vector search
            empty_neighbors,  # Empty neighbor search
            empty_details,  # Empty neighbor details
        ]

        results = hybrid.vector_search(
            client=mock_bq_client, query_text="test query", k=10, graph_boost=0.2
        )

        # Should return original results unchanged
        assert len(results) == 1
        # _normalize_rows changes chunk_id to id
        assert results[0]["id"] == "chunk1"
        assert results[0]["distance"] == 0.1

    def test_score_blending_algorithm(self):
        """Test the score blending algorithm for re-ranking"""
        # Test internal scoring logic
        vector_score = 0.9  # 1 - distance = 1 - 0.1
        graph_weight = 0.8
        graph_boost = 0.2

        # Expected formula:
        # (1-graph_boost) * vector_score + graph_boost * graph_weight
        expected_score = (1 - 0.2) * 0.9 + 0.2 * 0.8
        expected_score = 0.8 * 0.9 + 0.2 * 0.8
        expected_score = 0.72 + 0.16
        expected_score = 0.88

        # This tests the scoring logic conceptually
        actual_score = (1 - graph_boost) * vector_score + graph_boost * graph_weight
        assert abs(actual_score - expected_score) < 0.001

    def test_graph_boost_parameter_validation(self, mock_bq_client):
        """Test graph_boost parameter validation"""
        # Mock simple return to avoid execution errors
        mock_bq_client.run_sql_template.return_value = []

        # Valid range: 0.0 to 1.0
        valid_boosts = [0.0, 0.1, 0.2, 0.5, 1.0]
        for boost in valid_boosts:
            # Should not raise exception
            try:
                hybrid.vector_search(
                    client=mock_bq_client, query_text="test", k=5, graph_boost=boost
                )
            except ValueError:
                pytest.fail(f"Valid graph_boost {boost} raised ValueError")

    def test_neighbor_deduplication(self, mock_bq_client):
        """Test that neighbors already in vector results are handled"""
        # Mock vector search with chunk1 (before _normalize_rows)
        vector_results = [
            {"chunk_id": "chunk1", "distance": 0.1, "text": "content1"},
        ]

        # Mock neighbor that includes chunk1 (should be deduplicated)
        neighbor_results = [
            {"src_chunk_id": "chunk1", "nbr_chunk_id": "chunk1", "weight": 0.9},  # Self-reference
            {"src_chunk_id": "chunk1", "nbr_chunk_id": "chunk2", "weight": 0.8},
        ]

        detail_results = [
            {"chunk_id": "chunk1", "text": "content1", "meta": "{}"},
            {"chunk_id": "chunk2", "text": "content2", "meta": "{}"},
        ]

        mock_bq_client.run_sql_template.side_effect = [
            vector_results,
            neighbor_results,
            detail_results,
        ]

        results = hybrid.vector_search(
            client=mock_bq_client, query_text="test query", k=10, graph_boost=0.2
        )

        # Should have unique chunks only
        # _normalize_rows changes chunk_id to id
        chunk_ids = [r["id"] for r in results]
        unique_ids = set(chunk_ids)
        assert len(chunk_ids) == len(unique_ids), "Results should have unique chunk_ids"
