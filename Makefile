.ONESHELL:
SHELL := /bin/bash

VENV := env
PYTHON := $(VENV)/bin/python3
PIP := uv pip

NAME := main.py
MAP_FILE := ./maps/easy/01_linear_path.txt
DIRS_TO_CLEAN := __pycache__ .mypy_cache
FILES_TO_CLEAN := *.pyc
EXCLUDE_NAMES_FLAKE8 := $(VENV)
EXCLUDE_NAMES_MYPY := ^$(VENV)/
MAKEFLAGS += --no-print-directory
RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

define SETUP_ENV
	if [ -z "$$VIRTUAL_ENV" ]; then
		echo "No active virtual environment found.";
		$(MAKE) venv;
		echo "Activating...";
		echo;
		. $(VENV)/bin/activate;
	fi
endef

define CHECK_PYGAME
	PYGAME_HIDE_SUPPORT_PROMPT=1 $(PYTHON) -c "import pygame" 2>/dev/null || { \
		echo "pygame not found, running install..."; \
		$(MAKE) install; \
	}
endef

define CHECK_LINT_TOOLS
	$(PYTHON) -c "import mypy" >/dev/null 2>&1 || { \
		echo "mypy not found, installing..."; \
		$(PIP) install mypy; \
	}
	$(PYTHON) -c "import flake8" >/dev/null 2>&1 || { \
		echo "flake8 not found, installing..."; \
		$(PIP) install flake8; \
	}
endef

help:
	@echo "Start:"
	echo "                 make install"
	echo "                 make run [<map-filename>]"
	echo
	echo "Available targets:"
	echo "  install        Install dependencies and set up the virtual environment"
	echo "  run            Run the application (default map: $(MAP_FILE))"
	echo "  lint           Run flake8 and mypy checks"
	echo "  lint-strict    Run flake8 and strict mypy checks"
	echo "  clean          Remove caches and temporary files"
	echo "  fclean         clean + remove virtual environment folder"
	echo "  debug          Run the debugger"

install:
	@$(SETUP_ENV)
	@$(PIP) install -r requirements.txt
	@echo
	@echo "Done! To activate the virtual environment, run:"
	@echo "  source $(VENV)/bin/activate"

run:
	@$(SETUP_ENV)
	@$(CHECK_PYGAME)
	@MAP="$(if $(RUN_ARGS),$(firstword $(RUN_ARGS)),$(MAP_FILE))"
	PYGAME_HIDE_SUPPORT_PROMPT=1 $(PYTHON) $(NAME) "$$MAP"

debug:
	@$(SETUP_ENV)
	@MAP="$(if $(RUN_ARGS),$(firstword $(RUN_ARGS)),$(MAP_FILE))"
	echo "Entering debug mode..."
	$(PYTHON) -m pdb $(NAME) "$$MAP"

clean:
	@echo "Cleaning..."
	echo "Removing $(DIRS_TO_CLEAN) $(FILES_TO_CLEAN)"
	find . -mindepth 1 \( \
		-type d \( $(foreach d,$(DIRS_TO_CLEAN),-name "$(d)" -o ) -false \) -o \
		-type f \( $(foreach f,$(FILES_TO_CLEAN),-name "$(f)" -o ) -false \) \
	\) -exec rm -rf {} +
	echo "Cleaning is finished!"

fclean: clean
	@rm -fr $(VENV)
	echo "$(VENV) directory is removed"

re: fclean install

lint:
	@$(SETUP_ENV)
	@$(CHECK_LINT_TOOLS)
	echo "Checking with flake8..."
	$(PYTHON) -m flake8 . --exclude $(EXCLUDE_NAMES_FLAKE8)
	echo "flake8 check finished"
	echo "Checking with mypy..."
	$(PYTHON) -m mypy . --exclude $(EXCLUDE_NAMES_MYPY) --warn-return-any \
		--warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	@$(SETUP_ENV)
	@$(CHECK_LINT_TOOLS)
	echo "Checking with flake8..."
	$(PYTHON) -m flake8 . --exclude $(EXCLUDE_NAMES_FLAKE8)
	echo "flake8 check finished"
	echo "Checking with mypy --strict..."
	$(PYTHON) -m mypy . --exclude $(EXCLUDE_NAMES_MYPY) --strict

venv:
	@if [ ! -d "$(VENV)" ]; then
		echo "Creating virtual environment...";
		if command -v uv >/dev/null 2>&1; then
			uv -q venv --python 3.12 $(VENV);
		elif python3 -m venv --help >/dev/null 2>&1; then
			python3 -m venv $(VENV);
		else
			echo "Cannot create venv: neither 'uv' is installed nor 'python3 -m venv' is usable.";
			echo "No sudo available -> install uv in user space and re-run.";
			exit 1;
		fi;
	fi

%:
	@:

.PHONY: help install run debug clean fclean re lint lint-strict venv
