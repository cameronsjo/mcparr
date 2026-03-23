.DEFAULT_GOAL := help
PYTHON := uv run python
RUFF := uv run ruff
PYRIGHT := uv run pyright

## -- Development -------------------------------------------------------

.PHONY: dev
dev: ## Start development server (HTTP transport)
	$(PYTHON) -m mcparr

.PHONY: install
install: ## Install dependencies
	uv sync

## -- Quality -----------------------------------------------------------

.PHONY: check
check: lint typecheck ## Run all quality checks

.PHONY: lint
lint: ## Run ruff linter
	$(RUFF) check src/ tests/

.PHONY: typecheck
typecheck: ## Run pyright type checker
	$(PYRIGHT) src/

.PHONY: fix
fix: ## Auto-fix lint issues
	$(RUFF) check --fix src/ tests/
	$(RUFF) format src/ tests/

.PHONY: format
format: ## Format code
	$(RUFF) format src/ tests/

## -- Testing -----------------------------------------------------------

.PHONY: test
test: ## Run tests
	uv run pytest tests/ -v

## -- Docker ------------------------------------------------------------

.PHONY: docker-build
docker-build: ## Build Docker image
	docker build -t mcparr:local .

.PHONY: docker-run
docker-run: ## Run Docker container (requires .env file)
	docker run --rm --env-file .env -p 8080:8080 mcparr:local

## -- Help --------------------------------------------------------------

.PHONY: help
help: ## Show available targets (DEFAULT)
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
