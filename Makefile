lint: ISORT_CHECK_PARAMS := --diff --check-only
lint: BLACK_CHECK_PARAMS := --check --diff
lint: format flake8 mypy

format: isort black

isort:
	poetry run isort $(ISORT_CHECK_PARAMS) --settings-path ./ --recursive dge_ausgabeapp

black:
	poetry run black $(BLACK_CHECK_PARAMS) dge_ausgabeapp

flake8:
	poetry run flake8 dge_ausgabeapp

mypy:
	poetry run mypy dge_ausgabeapp


