.PHONY: test
test:
	PYTHONPATH=. python -m pytest -vv tests

.PHONY: lint
lint:
	PYTHONPATH=. python -m ruff check .
	PYTHONPATH=. python -m mypy src

.PHONY: run
run:
	PYTHONPATH=. python src/main.py
