"""Tests for BQ router module."""
from __future__ import annotations
import pytest
from unittest.mock import Mock
from bq.router import (
    predict_routing,
    train_router,
    check_router_model_exists,
    ROUTING_CONFIG,
    _heuristic_routing,
)


class TestHeuristicRouting:
    """Test rule-based routing fallback."""
    
    def test_logs_only_routing(self):
        """Test queries that should route to logs only."""
        query = "ERROR connection timeout database unavailable"
        config = _heuristic_routing(query)
        
        assert config["types"] == ["log"]
        assert config["k"] == 8
        assert "heuristic_meta" in config
        
    def test_pdf_image_routing(self):
        """Test queries that should route to pdf/image."""
        query = "document PDF page rendering issue screenshot"
        config = _heuristic_routing(query)
        
        assert config["types"] == ["pdf", "image", "image_ocr"]
        assert config["k"] == 6
        assert "heuristic_meta" in config
        
    def test_mixed_routing_long_query(self):
        """Test long queries that should use mixed routing."""
        query = "a" * 150  # Long query without specific keywords
        config = _heuristic_routing(query)
        
        assert config["types"] == []  # mixed = all types
        assert config["k"] == 10
        assert "heuristic_meta" in config
        
    def test_mixed_routing_default(self):
        """Test default mixed routing for ambiguous queries."""
        query = "generic issue"
        config = _heuristic_routing(query)
        
        assert config["types"] == []  # mixed = all types
        assert config["k"] == 10


class TestPredictRouting:
    """Test the predict_routing function with mocked client."""
    
    def test_heuristic_mode(self):
        """Test explicit heuristic mode."""
        mock_client = Mock()
        
        config, strategy = predict_routing(
            mock_client, "error timeout", "heuristic"
        )
        
        assert strategy == "heuristic"
        assert config["types"] == ["log"]
        assert "heuristic_meta" in config
        # Should not call BigQuery at all
        mock_client.run_sql_template.assert_not_called()
        
    def test_learned_mode_success(self):
        """Test learned mode with successful prediction."""
        mock_client = Mock()
        mock_client.run_sql_template.return_value = [{
            "predicted_label": "logs_only",
            "predicted_label_probs": [0.8, 0.1, 0.1]
        }]
        
        config, strategy = predict_routing(
            mock_client, "error timeout", "learned"
        )
        
        assert strategy == "learned"
        assert config["types"] == ["log"]
        assert "prediction_meta" in config
        assert config["prediction_meta"]["confidence"] == 0.8
        mock_client.run_sql_template.assert_called_once()
        
    def test_learned_mode_failure_fallback_disabled(self):
        """Test learned mode with failure and no fallback."""
        mock_client = Mock()
        mock_client.run_sql_template.side_effect = Exception("Model not found")
        
        with pytest.raises(RuntimeError, match="Learned routing required"):
            predict_routing(mock_client, "error timeout", "learned")
            
    def test_auto_mode_learned_success(self):
        """Test auto mode with successful learned routing."""
        mock_client = Mock()
        mock_client.run_sql_template.return_value = [{
            "predicted_label": "pdf_image",
            "predicted_label_probs": [0.1, 0.7, 0.2]
        }]
        
        config, strategy = predict_routing(
            mock_client, "pdf document", "auto"
        )
        
        assert strategy == "learned"
        assert config["types"] == ["pdf", "image", "image_ocr"]
        
    def test_auto_mode_fallback_to_heuristic(self):
        """Test auto mode falling back to heuristics."""
        mock_client = Mock()
        mock_client.run_sql_template.side_effect = Exception("Model not found")
        
        config, strategy = predict_routing(
            mock_client, "error timeout", "auto"
        )
        
        assert strategy == "heuristic"
        assert config["types"] == ["log"]
        assert "heuristic_meta" in config
        
    def test_invalid_predicted_label(self):
        """Test handling of invalid predicted labels."""
        mock_client = Mock()
        mock_client.run_sql_template.return_value = [{
            "predicted_label": "unknown_label",
            "predicted_label_probs": [0.5, 0.3, 0.2]
        }]
        
        config, strategy = predict_routing(
            mock_client, "some query", "auto"
        )
        
        # Should fall back to heuristics
        assert strategy == "heuristic"
        assert "heuristic_meta" in config


class TestModelManagement:
    """Test model training and existence checking."""
    
    def test_train_router_success(self):
        """Test successful router training."""
        mock_client = Mock()
        mock_client.run_sql_template.return_value = []
        
        result = train_router(mock_client)
        
        assert result is True
        # Should call create training data and train model
        assert mock_client.run_sql_template.call_count == 2
        
    def test_train_router_failure(self):
        """Test router training failure."""
        mock_client = Mock()
        mock_client.run_sql_template.side_effect = Exception("Training failed")
        
        result = train_router(mock_client)
        
        assert result is False
        
    def test_check_router_model_exists_true(self):
        """Test model existence check when model exists."""
        mock_client = Mock()
        mock_client.run_sql_template.return_value = []
        
        result = check_router_model_exists(mock_client)
        
        assert result is True
        
    def test_check_router_model_exists_false(self):
        """Test model existence check when model doesn't exist."""
        mock_client = Mock()
        mock_client.run_sql_template.side_effect = Exception("Model not found")
        
        result = check_router_model_exists(mock_client)
        
        assert result is False


class TestRoutingConfig:
    """Test routing configuration constants."""
    
    def test_routing_config_structure(self):
        """Test that routing config has expected structure."""
        for label, config in ROUTING_CONFIG.items():
            assert "types" in config
            assert "k" in config
            assert isinstance(config["types"], list)
            assert isinstance(config["k"], int)
            assert config["k"] > 0
            
    def test_routing_labels(self):
        """Test expected routing labels exist."""
        expected_labels = {"logs_only", "pdf_image", "mixed"}
        assert set(ROUTING_CONFIG.keys()) == expected_labels


# SQL template presence checks (static validation)
def test_sql_templates_exist():
    """Test that required SQL templates exist."""
    from pathlib import Path
    
    sql_dir = Path("sql")
    required_templates = [
        "router_train.sql",
        "router_predict.sql", 
        "create_router_training.sql"
    ]
    
    for template in required_templates:
        template_path = sql_dir / template
        assert template_path.exists(), f"Missing SQL template: {template}"
        
        # Basic content validation
        content = template_path.read_text()
        assert "${PROJECT_ID}" in content
        assert "${DATASET}" in content
