-- Create router training data with seed examples
-- Variables: ${PROJECT_ID}, ${DATASET}
-- Creates table with synthetic training data for router classification

CREATE OR REPLACE TABLE `${PROJECT_ID}.${DATASET}.router_training` AS
SELECT
  text,
  label
FROM UNNEST([
  -- logs_only examples
  STRUCT('ERROR connection timeout database unavailable' AS text, 'logs_only' AS label),
  STRUCT('WARN memory usage high heap overflow' AS text, 'logs_only' AS label),
  STRUCT('DEBUG authentication failed invalid token' AS text, 'logs_only' AS label),
  STRUCT('FATAL service crashed segmentation fault' AS text, 'logs_only' AS label),
  STRUCT('INFO startup completed listening port 8080' AS text, 'logs_only' AS label),
  STRUCT('Exception stack trace java.lang.NullPointerException' AS text, 'logs_only' AS label),
  STRUCT('Connection refused unable to connect to host' AS text, 'logs_only' AS label),
  STRUCT('Timeout waiting for response from upstream' AS text, 'logs_only' AS label),
  
  -- pdf_image examples
  STRUCT('document PDF page rendering issue blurry text' AS text, 'pdf_image' AS label),
  STRUCT('image upload screenshot attachment preview' AS text, 'pdf_image' AS label),
  STRUCT('manual user guide documentation section 4.2' AS text, 'pdf_image' AS label),
  STRUCT('diagram flowchart visualization chart report' AS text, 'pdf_image' AS label),
  STRUCT('form fillable PDF signature required validation' AS text, 'pdf_image' AS label),
  STRUCT('scan document OCR text extraction accuracy' AS text, 'pdf_image' AS label),
  STRUCT('certificate license agreement terms conditions' AS text, 'pdf_image' AS label),
  STRUCT('invoice receipt billing statement financial' AS text, 'pdf_image' AS label),
  
  -- mixed examples
  STRUCT('application error logs PDF export functionality fails' AS text, 'mixed' AS label),
  STRUCT('user manual installation guide with error messages' AS text, 'mixed' AS label),
  STRUCT('system documentation screenshots log file analysis' AS text, 'mixed' AS label),
  STRUCT('troubleshooting guide includes config files and images' AS text, 'mixed' AS label),
  STRUCT('incident report contains stack traces and diagrams' AS text, 'mixed' AS label),
  STRUCT('support ticket attachments logs screenshots PDFs' AS text, 'mixed' AS label),
  STRUCT('integration testing results with logs and charts' AS text, 'mixed' AS label),
  STRUCT('deployment documentation code samples error outputs' AS text, 'mixed' AS label)
]);
