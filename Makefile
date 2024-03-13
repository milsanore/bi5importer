#!make
SHELL:=/bin/bash

# pp - pretty print function
yellow := $(shell tput setaf 3)
normal := $(shell tput sgr0)
define pp
	@printf '$(yellow)$(1)$(normal)\n'
endef

.PHONY: help
help: Makefile
	@echo " Choose a command to run:"
	@sed -n 's/^##//p' $< | column -t -s ':' | sed -e 's/^/ /'

## withenv: 🍝 make executes every line as a new shell. this is a workaround. call like so: `make withenv RECIPE=setup`
.PHONY: withenv
withenv:
	test -e .env || cp .env.example .env
	. .venv/bin/activate
	bash -c 'set -o allexport; source .env; set +o allexport; make "$$RECIPE"'

## db: start a containerised database
.PHONY: db
db:
	docker compose -p bi5importer up -d

## setup: setup the service (venv, dependencies, db migration)
.PHONY: setup
setup:
	@echo "⏱ Setting up the service..."
	python3 -m venv .venv
	@echo "📦 Fetching dependencies..."
	. .venv/bin/activate; \
	pip install -r requirements.txt
	@echo "🪀 Applying database migrations..."
	. .env && yoyo apply --database postgresql://$$DB_USER:$$DB_PASSWORD@$$DB_HOST:$$DB_PORT/$$DB_NAME
	@echo "✅ Setup complete"

## run: go go go
.PHONY: run
run:
	. .venv/bin/activate; \
	python bi5importer.py --path=test_data
