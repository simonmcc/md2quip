VIRTUAL_ENV := $(shell poetry env info -p)
sources = md2quip

.PHONY: test format lint unittest coverage pre-commit clean
test: format lint unittest

format:
	isort $(sources) tests
	black $(sources) tests

lint:
	poetry install
	poetry run flake8 $(sources) tests
	poetry run mypy $(sources) tests

unittest:
	poetry install
	poetry run python -m unittest -v

coverage:
	pytest --cov=$(sources) --cov-branch --cov-report=term-missing tests

pre-commit:
	pre-commit run --all-files

requirements.txt: pyproject.toml poetry.lock
	poetry export -f requirements.txt --output requirements.txt

clean:
	rm -rf .mypy_cache .pytest_cache
	rm -rf *.egg-info
	rm -rf .tox dist site
	rm -rf coverage.xml .coverage
	rm -rf $(VIRTUAL_ENV)
