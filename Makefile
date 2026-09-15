.PHONY: install test benchmark api demo verify smoke-hubspot smoke-salesforce smoke-slack smoke-smtp

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

test:
	python -m pytest -q

benchmark:
	python evals/benchmark.py

api:
	uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

demo:
	python app.py

smoke-hubspot:
	python scripts/integration_smoke.py hubspot

smoke-salesforce:
	python scripts/integration_smoke.py salesforce

smoke-slack:
	python scripts/integration_smoke.py slack

smoke-smtp:
	python scripts/integration_smoke.py smtp

verify:
	python -m compileall -q src scripts
	python -m pytest -q
	python evals/benchmark.py
	python scripts/integration_smoke.py hubspot
	python scripts/integration_smoke.py salesforce
	python scripts/integration_smoke.py slack
	python scripts/integration_smoke.py smtp
