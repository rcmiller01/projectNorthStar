.PHONY: fmt lint test smoke notebook-validate smoke-live preflight create-remote-models

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

create-remote-models:
	@[ -n "$$PROJECT_ID" ] || (echo "Set PROJECT_ID"; exit 1)
	@[ -n "$$DATASET" ] || (echo "Set DATASET"; exit 1)
	@[ -n "$$LOCATION" ] || (echo "Set LOCATION (BQ dataset location)"; exit 1)
	@[ -n "$$EMBED_ENDPOINT" ] || EMBED_ENDPOINT=text-embedding-004; : $${EMBED_ENDPOINT:=text-embedding-004}
	@[ -n "$$TEXT_ENDPOINT" ] || TEXT_ENDPOINT=gemini-1.5-pro; : $${TEXT_ENDPOINT:=gemini-1.5-pro}
	@[ -n "$$VERTEX_REGION" ] || VERTEX_REGION=us-central1; : $${VERTEX_REGION:=us-central1}
	EMBED_MODEL_FQID=$${EMBED_MODEL_FQID:-$$PROJECT_ID.$$DATASET.embed_model}; \
	TEXT_MODEL_FQID=$${TEXT_MODEL_FQID:-$$PROJECT_ID.$$DATASET.text_model}; \
	bq query --location=$$LOCATION --use_legacy_sql=false \
	  --parameter=embed_model_fqid:STRING:"$$EMBED_MODEL_FQID" \
	  --parameter=embed_endpoint:STRING:"$$EMBED_ENDPOINT" \
	  --parameter=text_model_fqid:STRING:"$$TEXT_MODEL_FQID" \
	  --parameter=text_endpoint:STRING:"$$TEXT_ENDPOINT" \
	  --parameter=region:STRING:"$$VERTEX_REGION" \
	  < sql/create_remote_models.sql
	@echo "➡  Embedding model: $$EMBED_MODEL_FQID  (endpoint=$$EMBED_ENDPOINT)"
	@echo "➡  Text model:      $$TEXT_MODEL_FQID   (endpoint=$$TEXT_ENDPOINT)"
