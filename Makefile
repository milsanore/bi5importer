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

# ## withenv: 🍝 `make` executes every line as a new shell. this is a workaround. `make withenv RECIPE=init`
# .PHONY: withenv
# withenv:
# 	test -e .env || cp .env.example .env
# 	. .venv/bin/activate
# 	bash -c 'set -o allexport; source .env; set +o allexport; make "$$RECIPE"'

## db: 💾 start a containerised database
.PHONY: db
db:
	docker compose -p bi5importer up -d

## init: ⚙️
.PHONY: init
init:
	@echo "⏱ Intializing app..."
	python3 -m venv .venv
	@echo "📦 Fetching dependencies..."
	. .venv/bin/activate; \
	  pip install -r requirements.txt
	@echo "🪀 Applying database migrations..."
	. .env && yoyo apply --database postgresql://$$DB_USER:$$DB_PASSWORD@$$DB_HOST:$$DB_PORT/$$DB_NAME
	@echo "✅ Init complete"

## run: 💨
.PHONY: run
run:
	. .venv/bin/activate; \
	  python bi5importer.py --path=test_data

## test: 🧪
.PHONY: test
test:
	COVERAGE_FILE=coverage/.coverage \
	  pytest --cov=src --cov-report xml:coverage/cov.xml
