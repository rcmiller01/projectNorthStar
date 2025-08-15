.PHONY: fmt lint test smoke notebook-validate smoke-live preflight preflight-models create-remote-models destroy-remote-models ingest-samples dashboard create-views build-chunk-neighbors check setup-dev pre-commit-all setup-all demo eval sweep-secrets sweep-secrets-strict public-sweep release-dry-run release assets demo-assets which-mmdc arch-png arch-svg arch arch-clean arch-verify train-router

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

build-chunk-neighbors:
	@[ -n "$$PROJECT_ID" ] || (echo "Set PROJECT_ID"; exit 1)
	@[ -n "$$DATASET" ] || (echo "Set DATASET"; exit 1)
	@echo "Building chunk neighbor relationships..."
	@if [ "$$OS" = "Windows_NT" ]; then \
	  powershell -NoProfile -Command "$$content = Get-Content sql/chunk_neighbors_ddl.sql -Raw; $$content = $$content -replace '\\$$\\{PROJECT_ID\\}', \"$$env:PROJECT_ID\"; $$content = $$content -replace '\\$$\\{DATASET\\}', \"$$env:DATASET\"; bq query --use_legacy_sql=false \"$$content\""; \
	  powershell -NoProfile -Command "$$content = Get-Content sql/build_chunk_neighbors.sql -Raw; $$content = $$content -replace '\\$$\\{PROJECT_ID\\}', \"$$env:PROJECT_ID\"; $$content = $$content -replace '\\$$\\{DATASET\\}', \"$$env:DATASET\"; bq query --use_legacy_sql=false \"$$content\"; if ($$LASTEXITCODE -eq 0) { Write-Host '[graph] chunk_neighbors built' } else { exit $$LASTEXITCODE }"; \
	else \
	  sed "s/\$${PROJECT_ID}/$$PROJECT_ID/g; s/\$${DATASET}/$$DATASET/g" sql/chunk_neighbors_ddl.sql | bq query --use_legacy_sql=false; \
	  sed "s/\$${PROJECT_ID}/$$PROJECT_ID/g; s/\$${DATASET}/$$DATASET/g" sql/build_chunk_neighbors.sql | bq query --use_legacy_sql=false && echo "[graph] chunk_neighbors built"; \
	fi

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

public-sweep-suppress:
	python scripts/public_sweep.py --suppress-internal

release-dry-run:
	@[ -n "$$RELEASE_VERSION" ] || echo "(optional) RELEASE_VERSION not set; will bump patch" 1>&2 || true
	DRY_RUN=1 python scripts/release.py --part $${PART:-patch} --dry-run

release:
	@[ -n "$$RELEASE_VERSION" ] || echo "(no RELEASE_VERSION provided; bumping $$PART or patch)" 1>&2
	python scripts/release.py --part $${PART:-patch}

# Where your Mermaid source lives
ARCH_SRC := docs/architecture.mmd
ARCH_PNG := docs/architecture.png
ARCH_SVG := docs/architecture.svg

TMP_ARCH_DIR := .tmp_arch

# Helper: test if mmdc exists
which-mmdc:
	@command -v mmdc >/dev/null 2>&1 || { \
	  echo "[arch] mermaid-cli (mmdc) not found."; \
	  echo "      Install: npm i -g @mermaid-js/mermaid-cli"; \
	  exit 127; }

arch-png: which-mmdc
	mmdc -i $(ARCH_SRC) -o $(ARCH_PNG) -b transparent
	@echo "[arch] wrote $(ARCH_PNG)"

arch-svg: which-mmdc
	mmdc -i $(ARCH_SRC) -o $(ARCH_SVG)
	@echo "[arch] wrote $(ARCH_SVG)"

# Build both
arch: arch-png arch-svg
	@echo "[arch] all done"

# Optional clean
arch-clean:
	@rm -f $(ARCH_PNG) $(ARCH_SVG)
	@echo "[arch] removed generated images"

arch-verify: which-mmdc
	@rm -rf $(TMP_ARCH_DIR) && mkdir -p $(TMP_ARCH_DIR)
	@mmdc -i $(ARCH_SRC) -o $(TMP_ARCH_DIR)/architecture.png -b transparent
	@mmdc -i $(ARCH_SRC) -o $(TMP_ARCH_DIR)/architecture.svg
	@diff -q $(TMP_ARCH_DIR)/architecture.png $(ARCH_PNG) >/dev/null 2>&1 || \
	  (echo "[arch-verify] PNG out of date. Rebuild with 'make arch'."; exit 1)
	@diff -q $(TMP_ARCH_DIR)/architecture.svg $(ARCH_SVG) >/dev/null 2>&1 || \
	  (echo "[arch-verify] SVG out of date. Rebuild with 'make arch'."; exit 1)
	@rm -rf $(TMP_ARCH_DIR)
	@echo "[arch-verify] diagrams are up to date"

assets:
	python scripts/gen_assets.py
	@echo "[assets] dashboard.png + demo.pdf + demo.png + samples_demo_bundle.zip ready"

demo-assets: assets
	@echo "[demo-assets] regenerating assets..."
	@if [ "$$BIGQUERY_REAL" != "1" ]; then \
	  echo "[demo-assets] BIGQUERY_REAL!=1 (or unset) -> skipping live demo (set BIGQUERY_REAL=1 to enable)"; \
	  echo "[demo-assets] assets complete (demo skipped)"; \
	  exit 0; \
	fi
	@if [ -z "$$PROJECT_ID" ] || [ -z "$$DATASET" ] || [ -z "$$LOCATION" ]; then \
	  echo "[demo-assets] missing one of PROJECT_ID/DATASET/LOCATION -> skipping live demo"; \
	  echo "[demo-assets] set e.g.: export PROJECT_ID=bq_project_northstar DATASET=demo_ai LOCATION=US BIGQUERY_REAL=1"; \
	  exit 0; \
	fi
	@$(MAKE) demo
	@echo "[demo-assets] assets + end-to-end demo complete"

train-router:
	@[ -n "$$PROJECT_ID" ] || (echo "Set PROJECT_ID"; exit 1)
	@[ -n "$$DATASET" ] || (echo "Set DATASET"; exit 1)
	@echo "Training router model..."
	@if [ "$$OS" = "Windows_NT" ]; then \
	  powershell -NoProfile -Command "$$content = Get-Content sql/router_training_ddl.sql -Raw; $$content = $$content -replace '\\$$\\{PROJECT_ID\\}', \"$$env:PROJECT_ID\"; $$content = $$content -replace '\\$$\\{DATASET\\}', \"$$env:DATASET\"; bq query --use_legacy_sql=false \"$$content\""; \
	  powershell -NoProfile -Command "$$content = Get-Content sql/router_seed_training.sql -Raw; $$content = $$content -replace '\\$$\\{PROJECT_ID\\}', \"$$env:PROJECT_ID\"; $$content = $$content -replace '\\$$\\{DATASET\\}', \"$$env:DATASET\"; bq query --use_legacy_sql=false \"$$content\" || Write-Host 'Seed data insertion completed (may have duplicates)'"; \
	  powershell -NoProfile -Command "$$content = Get-Content sql/router_train.sql -Raw; $$content = $$content -replace '\\$$\\{PROJECT_ID\\}', \"$$env:PROJECT_ID\"; $$content = $$content -replace '\\$$\\{DATASET\\}', \"$$env:DATASET\"; bq query --use_legacy_sql=false \"$$content\"; if ($$LASTEXITCODE -eq 0) { Write-Host '[router] trained (or updated) $$env:PROJECT_ID.$$env:DATASET.router_m' } else { exit $$LASTEXITCODE }"; \
	else \
	  sed "s/\$${PROJECT_ID}/$$PROJECT_ID/g; s/\$${DATASET}/$$DATASET/g" sql/router_training_ddl.sql | bq query --use_legacy_sql=false; \
	  sed "s/\$${PROJECT_ID}/$$PROJECT_ID/g; s/\$${DATASET}/$$DATASET/g" sql/router_seed_training.sql | bq query --use_legacy_sql=false || true; \
	  sed "s/\$${PROJECT_ID}/$$PROJECT_ID/g; s/\$${DATASET}/$$DATASET/g" sql/router_train.sql | bq query --use_legacy_sql=false && echo "[router] trained (or updated) $$PROJECT_ID.$$DATASET.router_m"; \
	fi

router-train: train-router
