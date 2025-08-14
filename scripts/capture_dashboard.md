# Capture Dashboard Screenshot / GIF

1. Start the dashboard (uses current env or stub data if BIGQUERY_REAL not set):
```bash
make dashboard
```
2. In another terminal/window, navigate to the running Streamlit URL (typically http://localhost:8501).
3. Manually capture a screenshot (system tool, Snip & Sketch, etc.) focusing on:
   - Top Issues
   - Severity Trend
   - Duplicates
4. Save as `docs/dashboard.png` (add alt text if embedding elsewhere).
5. (Optional) Create a short GIF using a recorder tool (e.g., ScreenToGif, Kap) and save to `docs/dashboard.gif`.

No external capture dependencies are added to the project; keep assets lightweight.
