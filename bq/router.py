"""BigQuery ML router with safe fallback to heuristics.

Provides intelligent routing decisions for query types using BQML
logistic regression. Falls back gracefully to rule-based routing when
model is unavailable.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, Tuple
from .bigquery_client import BigQueryClientBase

logger = logging.getLogger(__name__)

# Routing strategy mappings
ROUTING_CONFIG = {
    "logs_only": {"types": ["log"], "k": 8},
    "pdf_image": {"types": ["pdf", "image", "image_ocr"], "k": 6},
    "mixed": {"types": [], "k": 10},  # empty types = all types
}

# Heuristic fallback keywords
LOG_KEYWORDS = [
    "error", "warn", "debug", "fatal", "exception", "stack", "trace",
    "timeout", "connection"
]
PDF_IMAGE_KEYWORDS = [
    "pdf", "document", "image", "screenshot", "manual", "guide", "diagram",
    "chart", "scan", "ocr"
]


def train_router(client: BigQueryClientBase) -> bool:
    """Train the router model using seed training data.
    
    Returns True if training succeeded, False otherwise.
    """
    try:
        # Create training data
        logger.info("Creating router training data...")
        client.run_sql_template("create_router_training.sql", {})
        
        # Train model
        logger.info("Training router model...")
        client.run_sql_template("router_train.sql", {})
        
        logger.info("Router model training completed successfully")
        return True
        
    except Exception as exc:
        logger.error(f"Router training failed: {exc}")
        return False


def predict_routing(
    client: BigQueryClientBase, query: str, mode: str = "auto"
) -> Tuple[Dict[str, Any], str]:
    """Predict routing strategy for a query.
    
    Parameters
    ----------
    client : BigQueryClientBase
        BigQuery client for model predictions
    query : str
        Query text to route
    mode : str
        Routing mode: 'auto', 'learned', or 'heuristic'
        
    Returns
    -------
    Tuple[Dict[str, Any], str]
        (routing_config, strategy_used)
        routing_config has keys: types (list), k (int)
        strategy_used is 'learned' or 'heuristic'
    """
    if mode == "heuristic":
        return _heuristic_routing(query), "heuristic"
    
    # Try learned routing first (auto or learned mode)
    if mode in ("auto", "learned"):
        try:
            rows = client.run_sql_template(
                "router_predict.sql", {"query_text": f"'{query}'"}
            )
            
            if rows:
                row = rows[0]
                predicted_label = row.get("predicted_label")
                predicted_probs = row.get("predicted_label_probs", [])
                
                if predicted_label in ROUTING_CONFIG:
                    config = ROUTING_CONFIG[predicted_label].copy()
                    
                    # Add prediction metadata for telemetry
                    max_prob = (
                        max(predicted_probs) if predicted_probs else 0.0
                    )
                    config["prediction_meta"] = {
                        "predicted_label": predicted_label,
                        "confidence": max_prob,
                        "all_probs": predicted_probs
                    }
                    
                    logger.info(
                        f"Router predicted: {predicted_label} "
                        f"(confidence: {max_prob:.3f})"
                    )
                    return config, "learned"
                    
        except Exception as exc:
            logger.warning(
                f"Learned routing failed, falling back to heuristics: {exc}"
            )
            
            # If mode is 'learned' only, fail instead of fallback
            if mode == "learned":
                raise RuntimeError(
                    f"Learned routing required but unavailable: {exc}"
                )
    
    # Fallback to heuristics
    return _heuristic_routing(query), "heuristic"


def _heuristic_routing(query: str) -> Dict[str, Any]:
    """Rule-based routing fallback logic."""
    query_lower = query.lower()
    
    # Count keyword matches
    log_matches = sum(1 for kw in LOG_KEYWORDS if kw in query_lower)
    pdf_image_matches = sum(
        1 for kw in PDF_IMAGE_KEYWORDS if kw in query_lower
    )
    
    # Simple decision tree
    if log_matches > pdf_image_matches and log_matches >= 2:
        strategy = "logs_only"
    elif pdf_image_matches > log_matches and pdf_image_matches >= 2:
        strategy = "pdf_image"
    elif len(query) > 100:  # Longer queries often need mixed search
        strategy = "mixed"
    else:
        strategy = "mixed"  # Default to mixed for safety
    
    config = ROUTING_CONFIG[strategy].copy()
    config["heuristic_meta"] = {
        "log_matches": log_matches,
        "pdf_image_matches": pdf_image_matches,
        "query_length": len(query),
        "strategy": strategy
    }
    
    return config


def check_router_model_exists(client: BigQueryClientBase) -> bool:
    """Check if the router model exists in BigQuery.
    
    Returns True if model exists and is accessible, False otherwise.
    """
    try:
        # Try a simple predict query to test model existence
        client.run_sql_template(
            "router_predict.sql", {"query_text": "'test'"}
        )
        return True
    except Exception:
        return False

# Reflection:
# BQML integration with graceful fallback pattern.
# Next improvement: active learning to retrain with user feedback.
