PATHS = dge_ausgabeapp tests

.PHONY: lint format isort black flake8 mypy

lint: ISORT_CHECK_PARAMS := --diff --check-only
lint: BLACK_CHECK_PARAMS := --check --diff
lint: format flake8 mypy

format: isort black

isort:
	poetry run isort $(ISORT_CHECK_PARAMS) --settings-path ./ --recursive $(PATHS)

black:
	poetry run black $(BLACK_CHECK_PARAMS) $(PATHS)

flake8:
	poetry run flake8 $(PATHS)

mypy:
	poetry run mypy $(PATHS)
