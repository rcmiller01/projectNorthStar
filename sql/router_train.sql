-- Router training SQL: Create BQML logistic regression model for routing decisions
-- Variables: ${PROJECT_ID}, ${DATASET}
-- Expects router_training table with columns: text (STRING), label (STRING)
-- Labels: 'logs_only', 'pdf_image', 'mixed'

CREATE OR REPLACE MODEL `${PROJECT_ID}.${DATASET}.router_m`
OPTIONS(
  model_type='logistic_reg',
  input_label_cols=['label'],
  auto_class_weights=true
) AS
SELECT
  text,
  label
FROM `${PROJECT_ID}.${DATASET}.router_training`
WHERE text IS NOT NULL AND label IS NOT NULL;
