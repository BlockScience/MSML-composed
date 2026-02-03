.PHONY: help install install-dev format lint type-check test test-cov clean pre-commit

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package
	uv pip install -e .

install-dev: ## Install package with dev dependencies
	uv pip install -e ".[dev]"
	pre-commit install

format: ## Format code (black + ruff isort)
	black src/ tests/
	ruff check --fix --select I src/ tests/

lint: ## Lint code (ruff)
	ruff check src/ tests/

type-check: ## Type check (mypy)
	mypy src/math_spec_mapping/

test: ## Run tests
	pytest tests/

test-cov: ## Run tests with coverage
	pytest tests/ --cov=math_spec_mapping --cov-report=term-missing --cov-report=html

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	rm -rf .mypy_cache .pytest_cache .ruff_cache htmlcov
	rm -rf __pycache__ src/math_spec_mapping/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

pre-commit: ## Install pre-commit hooks
	pre-commit install
