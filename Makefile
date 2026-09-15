.PHONY: install test benchmark api demo verify

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

verify:
	python -m compileall -q src
	python -m pytest -q
	python evals/benchmark.py
