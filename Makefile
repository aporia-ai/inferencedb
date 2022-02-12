SHELL := /bin/bash

install-deps:

	@echo [!] Installing Poetry
	@sudo apt install python3-setuptools
	@sudo pip3 install poetry --upgrade

	@echo [!] Installing Project
	@poetry install

lint:
	@echo [!] Running linter
	@poetry run flake8 .

	@echo [!] Running type checker
	@poetry run mypy .

test:
	@echo [!] Running tests
	@poetry run pytest

bump-version:
	@if [ -z $(NEW_VERSION) ]; then \
		echo ERROR: NEW_VERSION is not defined; \
		exit 1; \
	fi

	@poetry version $(NEW_VERSION) || true
	@git add pyproject.toml || true

release:
	@echo [!] Building python artifacts
	@poetry build

	@echo [!] Publishing python library
	@poetry publish --username=__token__ --password=$(PYPI_TOKEN)
