.PHONY: install test benchmark agent-eval live-eval-dry analytics-report api demo verify deployment-check slo-dry release-version release-evidence release-verify smoke-hubspot smoke-salesforce smoke-slack smoke-smtp smoke-ai smoke-workflow smoke-reliability smoke-analytics

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

test:
	python -m pytest -q

benchmark:
	python evals/benchmark.py

agent-eval:
	python evals/agent_release_gate.py --report agent-eval-report.json

live-eval-dry:
	python evals/live_agent_eval.py openai
	python evals/live_agent_eval.py anthropic
	python evals/live_agent_eval.py gemini

analytics-report:
	python scripts/analytics_report.py

deployment-check:
	python scripts/deployment_contract.py

slo-dry:
	python scripts/slo_probe.py

release-version:
	python scripts/release_version_check.py

release-evidence:
	python scripts/release_evidence.py --output release-evidence

release-verify:
	python scripts/verify_release_evidence.py release-evidence

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
smoke-analytics:
	python scripts/analytics_smoke.py

verify:
	python -m compileall -q src scripts evals
	python -m pytest -q
	python evals/benchmark.py
	python evals/agent_release_gate.py --report agent-eval-report.json
	python evals/live_agent_eval.py openai
	python evals/live_agent_eval.py anthropic
	python evals/live_agent_eval.py gemini
	python scripts/integration_smoke.py hubspot
	python scripts/integration_smoke.py salesforce
	python scripts/integration_smoke.py slack
	python scripts/integration_smoke.py smtp
	python scripts/ai_provider_smoke.py openai
	python scripts/ai_provider_smoke.py anthropic
	python scripts/ai_provider_smoke.py gemini
	python scripts/workflow_smoke.py
	python scripts/reliability_smoke.py
	python scripts/analytics_smoke.py
	python scripts/deployment_contract.py
	python scripts/slo_probe.py
	python scripts/release_version_check.py
	python scripts/release_evidence.py --output release-evidence
	python scripts/verify_release_evidence.py release-evidence
