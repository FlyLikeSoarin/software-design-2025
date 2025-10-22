.PHONY: test
test:
	PYTHONPATH=. python -m pytest -vv tests

.PHONY: lint
lint:
	PYTHONPATH=. python -m ruff check .

.PHONY: run
run:
	PYTHONPATH=. python src/main.py
