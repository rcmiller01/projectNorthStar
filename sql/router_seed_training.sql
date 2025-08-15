-- Router seed training data
-- Variables: ${PROJECT_ID}, ${DATASET}
-- Provides minimal synthetic training examples

INSERT INTO `${PROJECT_ID}.${DATASET}.router_training` (text, label)
VALUES
  ('ERROR timeout [auth] 500 trace', 'logs_only'),
  ('see attached pdf and screenshot camera issue', 'pdf_image'),
  ('api error after upload; screenshot and logs show failure', 'mixed'),
  ('database connection failed with timeout error', 'logs_only'),
  ('check the user manual PDF for setup instructions', 'pdf_image'),
  ('upload error with server logs and image attachment', 'mixed'),
  ('stack trace shows null pointer exception', 'logs_only'),
  ('diagram in documentation shows incorrect flow', 'pdf_image'),
  ('error occurs during file upload with debug logs', 'mixed');
