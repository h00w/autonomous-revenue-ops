.PHONY: install test benchmark api demo verify smoke-hubspot smoke-salesforce smoke-slack smoke-smtp smoke-ai smoke-workflow smoke-reliability

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
smoke-ai:
	python scripts/ai_provider_smoke.py openai
	python scripts/ai_provider_smoke.py anthropic
	python scripts/ai_provider_smoke.py gemini
smoke-workflow:
	python scripts/workflow_smoke.py
smoke-reliability:
	python scripts/reliability_smoke.py

verify:
	python -m compileall -q src scripts
	python -m pytest -q
	python evals/benchmark.py
	python scripts/integration_smoke.py hubspot
	python scripts/integration_smoke.py salesforce
	python scripts/integration_smoke.py slack
	python scripts/integration_smoke.py smtp
	python scripts/ai_provider_smoke.py openai
	python scripts/ai_provider_smoke.py anthropic
	python scripts/ai_provider_smoke.py gemini
	python scripts/workflow_smoke.py
	python scripts/reliability_smoke.py
