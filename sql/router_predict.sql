-- Router prediction SQL: Predict routing strategy using trained BQML model
-- Variables: ${PROJECT_ID}, ${DATASET}, ${QUERY_TEXT}
-- Returns: predicted_label, predicted_label_probs for routing decision

SELECT
  predicted_label,
  predicted_label_probs
FROM ML.PREDICT(
  MODEL `${PROJECT_ID}.${DATASET}.router_m`,
  (SELECT ${QUERY_TEXT} AS text)
);
