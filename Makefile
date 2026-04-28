.PHONY: install run debug clean lint lint-strict

# Define environment variables

PYTHON_BIN = poetry run python
PACKAGE_MANAGER = poetry

install: PACKAGE_MANAGER


# Clean up all generated files, including the virtual environment and dist folders
clean:
	rm -rf __pycache__
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Helper to ensure the virtual environment exists before linting
installation_check:
	@test -d $(VENV) || (echo "Virtual environment not found. Run 'make install' first." && exit 1)

lint: installation_check
	@$(PYTHON) -m flake8 --exclude .venv,venv,env .
	@$(PYTHON) -m mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict: installation_check
	@$(PYTHON) -m flake8 --exclude .venv,venv,env .
	@$(PYTHON) -m mypy . --strict
