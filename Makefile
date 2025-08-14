.PHONY: fmt lint test smoke notebook-validate smoke-live preflight preflight-models create-remote-models destroy-remote-models ingest-samples

fmt:
	ruff --fix .
	black .

lint:
	ruff .
	black --check .

test:
	pytest -q

smoke:
	python -m core.cli triage --title "Login 500" --body "after reset" --out out/smoke.md

notebook-validate:
	python scripts/validate_phase0.py

smoke-live:
	BIGQUERY_REAL=1 \
	PROJECT_ID=$${PROJECT_ID:-bq_project_northstar} \
	DATASET=$${DATASET:-demo_ai} \
	LOCATION=$${LOCATION:-US} \
	python -m core.cli triage --title "Image upload fails" --body "content-type mismatch" --out out/smoke_live.md

preflight:
	python scripts/check_bq_resources.py

preflight-models:
	python scripts/check_bq_resources.py --models-only

create-remote-models:
	@[ -n "$$PROJECT_ID" ] || (echo "Set PROJECT_ID"; exit 1)
	@[ -n "$$DATASET" ] || (echo "Set DATASET"; exit 1)
	@[ -n "$$LOCATION" ] || (echo "Set LOCATION (BQ dataset location)"; exit 1)
	python scripts/create_remote_models.py

destroy-remote-models:
	@echo "Remote model teardown requested"
	@if [ "$$OS" = "Windows_NT" ]; then \
	  powershell -NoProfile -Command "if (-not $$env:FORCE -or $$env:FORCE -ne '1') { Write-Host 'Refusing to destroy without FORCE=1'; exit 2 }; $$c = Get-Content sql/drop_remote_models.sql -Raw; bq query --use_legacy_sql=false \"$$c\"; if ($$LASTEXITCODE -eq 0) { Write-Host '✅ Drop attempted (Windows)'} else { exit $$LASTEXITCODE }"; \
	else \
	  if [ "$$FORCE" != "1" ]; then echo "Refusing to destroy without FORCE=1"; exit 2; fi; \
	  bq query --use_legacy_sql=false "$$(cat sql/drop_remote_models.sql)" && echo "✅ Drop attempted"; \
	fi

ingest-samples:
	python -m core.cli ingest --path samples --type auto --max-tokens 512

refresh-all:
	python scripts/refresh_all.py
