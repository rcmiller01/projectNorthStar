.PHONY: fmt lint test smoke notebook-validate smoke-live preflight preflight-models create-remote-models destroy-remote-models ingest-samples dashboard create-views check setup-dev pre-commit-all setup-all demo eval sweep-secrets sweep-secrets-strict public-sweep release-dry-run release

fmt:
	ruff --fix .
	black .

lint:
	ruff .
	black --check .

test:
	pytest -q

check: fmt lint test

setup-dev:
	pip install -e .[dev]
	pre-commit install || echo "pre-commit not installed in environment"

pre-commit-all:
	pre-commit run --all-files || echo "pre-commit hook run completed with above status"

setup-all:
	pip install -e .[bigquery,ingest,dashboard,dev]
	pre-commit install || echo "pre-commit install skipped"

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

dashboard:
	streamlit run src/dashboard/app.py

create-views:
	@[ -n "$$PROJECT_ID" ] || (echo "Set PROJECT_ID"; exit 1)
	@[ -n "$$DATASET" ] || (echo "Set DATASET"; exit 1)
	@[ -n "$$LOCATION" ] || (echo "Set LOCATION"; exit 1)
	python scripts/create_views.py

demo:
	@[ -n "$$PROJECT_ID" ] || (echo "Set PROJECT_ID"; exit 1)
	@[ -n "$$DATASET" ] || (echo "Set DATASET"; exit 1)
	@[ -n "$$LOCATION" ] || (echo "Set LOCATION"; exit 1)
	@[ "$$BIGQUERY_REAL" = "1" ] || (echo "Set BIGQUERY_REAL=1 for live demo"; exit 1)
	python scripts/demo_end_to_end.py

eval:
	python scripts/gen_eval_set.py
	python scripts/run_eval.py --top-k 5 --output metrics/eval_results.json

eval-ci:
	python scripts/gen_eval_set.py
	python scripts/run_eval.py --top-k 5 --output metrics/eval_results.json --use-stub
	python scripts/metrics_trend.py

sweep-secrets:
	python scripts/secret_sweep.py

sweep-secrets-strict:
	python scripts/secret_sweep.py --fail-on=MED

public-sweep:
	python scripts/public_sweep.py

release-dry-run:
	@[ -n "$$RELEASE_VERSION" ] || echo "(optional) RELEASE_VERSION not set; will bump patch" 1>&2 || true
	DRY_RUN=1 python scripts/release.py --part $${PART:-patch} --dry-run

release:
	@[ -n "$$RELEASE_VERSION" ] || echo "(no RELEASE_VERSION provided; bumping $$PART or patch)" 1>&2
	python scripts/release.py --part $${PART:-patch}
