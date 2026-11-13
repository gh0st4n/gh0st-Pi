#!/usr/bin/env bash
# ============================================================================
# HexStrike AI - Master Test Runner
# Menjalankan semua test secara bertahap
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Warna
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

PYTHON_BIN=".venv/bin/python"
SERVER_URL="http://127.0.0.1:8888"
SERVER_PID=""
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

# ─── Helper ───────────────────────────────────────────────────────────────────
log_step()    { echo -e "\n${PURPLE}${BOLD}════════════════════════════════════════════════════${NC}"; echo -e "${PURPLE}${BOLD}  $1${NC}"; echo -e "${PURPLE}${BOLD}════════════════════════════════════════════════════${NC}\n"; }
log_pass()    { echo -e "  ${GREEN}✅ $1${NC}"; ((PASS_COUNT++)); }
log_fail()    { echo -e "  ${RED}❌ $1${NC}"; ((FAIL_COUNT++)); }
log_skip()    { echo -e "  ${YELLOW}⏭️  $1${NC}"; ((SKIP_COUNT++)); }
log_info()    { echo -e "  ${BLUE}ℹ️  $1${NC}"; }

banner() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║     🔥 HexStrike AI - Test Suite 🔥                         ║"
    echo "║     Comprehensive Testing with uv                           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

cleanup() {
    if [ -n "$SERVER_PID" ]; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
        echo -e "\n${YELLOW}Server stopped${NC}"
    fi
}
trap cleanup EXIT

# ─── Phase 1: Pre-checks ─────────────────────────────────────────────────────
phase_prechecks() {
    log_step "PHASE 1: Pre-checks"

    # Cek venv ada
    if [ ! -f "$PYTHON_BIN" ]; then
        log_fail "Virtual environment tidak ditemukan. Jalankan ./setup.sh dulu"
        exit 1
    fi
    log_pass "Virtual environment ditemukan"

    # Cek uv
    if command -v uv &>/dev/null; then
        log_pass "uv tersedia: $(uv --version)"
    else
        log_fail "uv tidak ditemukan"
        exit 1
    fi

    # Cek hexstrike package
    if "$PYTHON_BIN" -c "import hexstrike" 2>/dev/null; then
        log_pass "hexstrike package bisa diimport"
    else
        log_fail "hexstrike package tidak bisa diimport"
        exit 1
    fi
}

# ─── Phase 2: Syntax Check ────────────────────────────────────────────────────
phase_syntax_check() {
    log_step "PHASE 2: Syntax Check"

    local total=0
    local errors=0

    while IFS= read -r -d '' file; do
        ((total++))
        if ! "$PYTHON_BIN" -m py_compile "$file" 2>/dev/null; then
            log_fail "Syntax error: $file"
            ((errors++))
        fi
    done < <(find hexstrike hexstrike_server.py hexstrike_mcp.py -name "*.py" -print0 2>/dev/null)

    if [ $errors -eq 0 ]; then
        log_pass "Semua $total file syntax OK"
    else
        log_fail "$errors dari $total file memiliki syntax error"
        return 1
    fi
}

# ─── Phase 3: Import Tests ────────────────────────────────────────────────────
phase_import_tests() {
    log_step "PHASE 3: Import Tests"

    local modules=(
        "hexstrike"
        "hexstrike.config"
        "hexstrike.core.colors"
        "hexstrike.core.cache"
        "hexstrike.core.telemetry"
        "hexstrike.core.executor"
        "hexstrike.core.process_manager"
        "hexstrike.core.visual_engine"
        "hexstrike.core.logging"
        "hexstrike.intelligence.models"
        "hexstrike.intelligence.decision_engine"
        "hexstrike.intelligence.parameter_optimizer"
        "hexstrike.intelligence.technology_detector"
        "hexstrike.intelligence.rate_limiter"
        "hexstrike.error_handling.models"
        "hexstrike.error_handling.handler"
        "hexstrike.error_handling.recovery"
        "hexstrike.error_handling.degradation"
        "hexstrike.workflows.bugbounty"
        "hexstrike.workflows.ctf_manager"
        "hexstrike.workflows.ctf_tools"
        "hexstrike.workflows.ctf_automation"
        "hexstrike.workflows.ctf_team"
        "hexstrike.vuln_intel.cve_manager"
        "hexstrike.vuln_intel.exploit_generator"
        "hexstrike.vuln_intel.correlator"
        "hexstrike.web_testing.http_framework"
        "hexstrike.web_testing.payload_generator"
        "hexstrike.infrastructure.process_pool"
        "hexstrike.infrastructure.resource_monitor"
        "hexstrike.infrastructure.performance"
        "hexstrike.infrastructure.env_manager"
        "hexstrike.utils.file_ops"
    )

    for module in "${modules[@]}"; do
        if "$PYTHON_BIN" -c "import $module" 2>/dev/null; then
            log_pass "import $module"
        else
            log_fail "import $module"
        fi
    done

    # Flask & MCP imports (conditional, mungkin butuh deps ekstra)
    if "$PYTHON_BIN" -c "from flask import Flask" 2>/dev/null; then
        log_pass "import flask"
    else
        log_skip "import flask (belum terinstall)"
    fi

    if "$PYTHON_BIN" -c "from mcp.server.fastmcp import FastMCP" 2>/dev/null; then
        log_pass "import fastmcp"
    else
        log_skip "import fastmcp (belum terinstall)"
    fi
}

# ─── Phase 4: Unit Tests (pytest) ────────────────────────────────────────────
phase_unit_tests() {
    log_step "PHASE 4: Unit Tests (pytest)"

    if [ -d "tests" ] && [ -n "$(find tests -name 'test_*.py' -print -quit 2>/dev/null)" ]; then
        if uv run pytest tests/ -v --tb=short -x -m "unit or not integration and not e2e" 2>&1 | tee /tmp/pytest_output.log; then
            log_pass "Unit tests passed"
        else
            log_fail "Unit tests failed (lihat output di atas)"
        fi
    else
        log_skip "Belum ada unit tests di folder tests/"
        log_info "Buat file tests/test_*.py untuk unit tests"
    fi
}

# ─── Phase 5: Linting ────────────────────────────────────────────────────────
phase_linting() {
    log_step "PHASE 5: Linting (ruff)"

    if uv run ruff check hexstrike/ --output-format=concise 2>&1 | head -30; then
        log_pass "Ruff linting passed"
    else
        log_warn "Ruff menemukan issues (bukan blocking)"
    fi
}

# ─── Phase 6: Server Startup Test ────────────────────────────────────────────
phase_server_test() {
    log_step "PHASE 6: Server Startup Test"

    log_info "Starting server di background..."
    uv run python hexstrike_server.py &
    SERVER_PID=$!

    # Wait server ready
    local max_wait=30
    local waited=0
    while [ $waited -lt $max_wait ]; do
        if curl -s -o /dev/null "$SERVER_URL/health" 2>/dev/null; then
            log_pass "Server ready dalam ${waited}s"
            break
        fi
        sleep 1
        ((waited++))
    done

    if [ $waited -ge $max_wait ]; then
        log_fail "Server tidak ready dalam ${max_wait}s"
        return 1
    fi

    # Test health endpoint
    local health_response
    health_response=$(curl -s "$SERVER_URL/health")
    if echo "$health_response" | grep -q '"status"'; then
        log_pass "GET /health → 200 OK"
    else
        log_fail "GET /health → response tidak valid"
    fi

    # Test command endpoint
    local cmd_response
    cmd_response=$(curl -s -X POST "$SERVER_URL/api/command" \
        -H "Content-Type: application/json" \
        -d '{"command": "echo hello"}')
    if echo "$cmd_response" | grep -q "success\|stdout"; then
        log_pass "POST /api/command → OK"
    else
        log_fail "POST /api/command → response tidak valid"
    fi

    # Test intelligence endpoint
    local intel_response
    intel_response=$(curl -s -X POST "$SERVER_URL/api/intelligence/analyze-target" \
        -H "Content-Type: application/json" \
        -d '{"target": "http://example.com"}')
    if echo "$intel_response" | grep -q "success\|target_profile"; then
        log_pass "POST /api/intelligence/analyze-target → OK"
    else
        log_fail "POST /api/intelligence/analyze-target → gagal"
    fi

    # Test error handling endpoint
    local err_response
    err_response=$(curl -s "$SERVER_URL/api/error-handling/statistics")
    if echo "$err_response" | grep -q "success\|statistics"; then
        log_pass "GET /api/error-handling/statistics → OK"
    else
        log_fail "GET /api/error-handling/statistics → gagal"
    fi

    # Test visual endpoint
    local visual_response
    visual_response=$(curl -s -X POST "$SERVER_URL/api/visual/vulnerability-card" \
        -H "Content-Type: application/json" \
        -d '{"name": "Test Vuln", "severity": "high", "description": "Test description"}')
    if echo "$visual_response" | grep -q "success\|vulnerability_card"; then
        log_pass "POST /api/visual/vulnerability-card → OK"
    else
        log_fail "POST /api/visual/vulnerability-card → gagal"
    fi
}

# ─── Phase 7: API Endpoints Comprehensive Test ───────────────────────────────
phase_api_comprehensive() {
    log_step "PHASE 7: API Endpoints Comprehensive"

    if [ -z "$SERVER_PID" ]; then
        log_skip "Server tidak running, skip API tests"
        return 0
    fi

    local endpoints=(
        "GET|/health"
        "POST|/api/command|{\"command\":\"echo test\"}"
        "POST|/api/files/create|{\"filename\":\"test.txt\",\"content\":\"hello\"}"
        "GET|/api/files/list"
        "POST|/api/files/delete|{\"filename\":\"test.txt\"}"
        "POST|/api/intelligence/analyze-target|{\"target\":\"192.168.1.1\"}"
        "POST|/api/intelligence/select-tools|{\"target\":\"192.168.1.1\",\"objective\":\"quick\"}"
        "POST|/api/intelligence/technology-detection|{\"target\":\"http://example.com\"}"
        "POST|/api/bugbounty/reconnaissance-workflow|{\"domain\":\"example.com\"}"
        "POST|/api/bugbounty/vulnerability-hunting-workflow|{\"domain\":\"example.com\"}"
        "POST|/api/ctf/create-challenge-workflow|{\"name\":\"test\",\"category\":\"web\",\"difficulty\":\"easy\"}"
        "POST|/api/ctf/suggest-tools|{\"description\":\"SQL injection\",\"category\":\"web\"}"
        "POST|/api/vuln-intel/attack-chains|{\"target_software\":\"nginx\"}"
        "POST|/api/vuln-intel/threat-feeds|{\"indicators\":[\"CVE-2024-1234\"]}"
        "GET|/api/error-handling/statistics"
        "POST|/api/error-handling/test-recovery|{\"tool_name\":\"nmap\",\"error_type\":\"timeout\"}"
        "POST|/api/visual/vulnerability-card|{\"name\":\"SQLi\",\"severity\":\"critical\",\"description\":\"Found\"}"
        "POST|/api/visual/summary-report|{\"target\":\"test.com\",\"vulnerabilities\":[],\"tools_used\":[\"nmap\"]}"
        "GET|/api/processes/list"
        "GET|/api/processes/dashboard"
    )

    for endpoint_data in "${endpoints[@]}"; do
        IFS='|' read -r method url data <<< "$endpoint_data"

        local http_code
        if [ "$method" = "GET" ]; then
            http_code=$(curl -s -o /dev/null -w "%{http_code}" "${SERVER_URL}${url}" --max-time 10)
        else
            http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
                -H "Content-Type: application/json" \
                -d "$data" "${SERVER_URL}${url}" --max-time 10)
        fi

        if [ "$http_code" = "200" ]; then
            log_pass "$method $url → $http_code"
        else
            log_fail "$method $url → $http_code"
        fi
    done
}

# ─── Phase 8: MCP Client Test ────────────────────────────────────────────────
phase_mcp_test() {
    log_step "PHASE 8: MCP Client Test"

    if [ -z "$SERVER_PID" ]; then
        log_skip "Server tidak running, skip MCP test"
        return 0
    fi

    log_info "Testing MCP client connection..."

    # Test MCP client bisa start (timeout 10 detik)
    if timeout 10 uv run python hexstrike_mcp.py --server "$SERVER_URL" 2>&1 | head -20; then
        log_pass "MCP client bisa start dan connect"
    else
        log_warn "MCP client timeout (normal untuk stdio server, bukan error)"
    fi
}

# ─── Summary ──────────────────────────────────────────────────────────────────
show_summary() {
    echo -e "\n${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    📊 TEST SUMMARY                           ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo -e "║  ${GREEN}✅ Passed${NC}: ${GREEN}${PASS_COUNT}${NC}                                             ║"
    echo -e "║  ${RED}❌ Failed${NC}: ${RED}${FAIL_COUNT}${NC}                                             ║"
    echo -e "║  ${YELLOW}⏭️  Skipped${NC}: ${YELLOW}${SKIP_COUNT}${NC}                                             ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    if [ $FAIL_COUNT -eq 0 ]; then
        echo -e "║  ${GREEN}${BOLD}🎉 SEMUA TEST BERHASIL!${NC}                                    ║"
    else
        echo -e "║  ${RED}${BOLD}⚠️  ADA TEST YANG GAGAL${NC}                                    ║"
    fi
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
    banner

    phase_prechecks       || true
    phase_syntax_check    || true
    phase_import_tests    || true
    phase_unit_tests      || true
    phase_linting         || true
    phase_server_test     || true
    phase_api_comprehensive || true
    phase_mcp_test        || true

    show_summary

    # Exit code berdasarkan hasil
    if [ $FAIL_COUNT -gt 0 ]; then
        exit 1
    fi
    exit 0
}

main "$@"