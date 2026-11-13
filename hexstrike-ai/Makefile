# ============================================================================
# HexStrike AI - Makefile
# ============================================================================

PYTHON     := .venv/bin/python
UV         := uv
SERVER_URL := http://127.0.0.1:8888

.PHONY: help setup server mcp test test-unit test-api test-e2e lint clean install-tools

# ─── Help ─────────────────────────────────────────────────────────────────────
help: ## Tampilkan bantuan
	@echo "╔══════════════════════════════════════════════════╗"
	@echo "║   HexStrike AI - Available Commands              ║"
	@echo "╠══════════════════════════════════════════════════╣"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "║  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo "╚══════════════════════════════════════════════════╝"

# ─── Setup ────────────────────────────────────────────────────────────────────
setup: ## Setup environment lengkap
	./setup.sh

install: ## Install dependencies saja
	$(UV) pip install --python $(PYTHON) -e ".[dev]"

install-full: ## Install semua dependencies (termasuk binary tools)
	$(UV) pip install --python $(PYTHON) -e ".[full]"

# ─── Run ──────────────────────────────────────────────────────────────────────
server: ## Start HexStrike server
	$(UV) run python hexstrike_server.py

server-debug: ## Start server dengan debug mode
	$(UV) run python hexstrike_server.py --debug

mcp: ## Start MCP client (butuh server running)
	$(UV) run python hexstrike_mcp.py --server $(SERVER_URL)

mcp-debug: ## Start MCP client dengan debug
	$(UV) run python hexstrike_mcp.py --server $(SERVER_URL) --debug

# ─── Testing ──────────────────────────────────────────────────────────────────
test: ## Run semua tests
	./test_all.sh

test-unit: ## Run unit tests saja
	$(UV) run pytest tests/ -v -m unit --tb=short

test-imports: ## Test imports saja
	$(UV) run pytest tests/test_imports.py -v

test-api: ## Test API endpoints (butuh server running)
	$(UV) run pytest tests/ -v -m integration --tb=short

test-e2e: ## End-to-end test
	$(UV) run python tests/test_e2e.py

test-cov: ## Run tests dengan coverage report
	$(UV) run pytest tests/ --cov=hexstrike --cov-report=term-missing

# ─── Quality ──────────────────────────────────────────────────────────────────
lint: ## Run linter (ruff)
	$(UV) run ruff check hexstrike/

lint-fix: ## Run linter dengan auto-fix
	$(UV) run ruff check hexstrike/ --fix

format: ## Format code (ruff)
	$(UV) run ruff format hexstrike/

syntax-check: ## Cek syntax semua file Python
	@find hexstrike hexstrike_server.py hexstrike_mcp.py -name "*.py" \
		-exec $(PYTHON) -m py_compile {} \; && echo "✅ Syntax OK"

# ─── Cleanup ──────────────────────────────────────────────────────────────────
clean: ## Cleanup cache & temp files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	@echo "✅ Cleanup done"

clean-all: clean ## Cleanup + hapus venv
	rm -rf .venv
	@echo "✅ Virtual environment dihapus"

rebuild: clean-all setup ## Rebuild dari awal