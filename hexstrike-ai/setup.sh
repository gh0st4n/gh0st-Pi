#!/usr/bin/env bash
# ============================================================================
# HexStrike AI - Setup Script dengan uv
# Python Package Manager super cepat
# ============================================================================
set -euo pipefail

# ─── Konfigurasi ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR=".venv"
PYTHON_MIN_VERSION="3.10"
UV_VERSION_MIN="0.4.0"

# Warna terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ─── Fungsi Helper ───────────────────────────────────────────────────────────
log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()    { echo -e "\n${PURPLE}${BOLD}━━━ $1 ━━━${NC}"; }

banner() {
    echo -e "${RED}${BOLD}"
    cat << 'EOF'
██╗  ██╗███████╗██╗  ██╗███████╗████████╗██████╗ ██╗██╗  ██╗███████╗
██║  ██║██╔════╝╚██╗██╔╝██╔════╝╚══██╔══╝██╔══██╗██║██║ ██╔╝██╔════╝
███████║█████╗   ╚███╔╝ ███████╗   ██║   ██████╔╝██║█████╔╝ █████╗
██╔══██║██╔══╝   ██╔██╗ ╚════██║   ██║   ██╔══██╗██║██╔═██╗ ██╔══╝
██║  ██║███████╗██╔╝ ██╗███████║   ██║   ██║  ██║██║██║  ██╗███████╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝
EOF
    echo -e "${NC}"
    echo -e "${CYAN}  🔥 Setup Environment dengan uv 🔥${NC}"
    echo -e "${CYAN}  📦 Advanced Penetration Testing Framework v6.0${NC}\n"
}

# ─── Step 0: Preflight Checks ────────────────────────────────────────────────
check_prerequisites() {
    log_step "Step 0: Preflight Checks"

    # Cek Python
    if ! command -v python3 &>/dev/null; then
        log_error "python3 tidak ditemukan!"
        log_info "Install Python ${PYTHON_MIN_VERSION}+: sudo apt install python3 python3-pip python3-venv"
        exit 1
    fi

    local py_version
    py_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "Python version: $py_version"

    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
        log_error "Python ${PYTHON_MIN_VERSION}+ diperlukan. Versi saat ini: $py_version"
        exit 1
    fi
    log_success "Python $py_version memenuhi syarat"

    # Cek uv
    if ! command -v uv &>/dev/null; then
        log_warn "uv tidak ditemukan. Installing..."
        install_uv
    fi

    local uv_version
    uv_version=$(uv --version | awk '{print $2}')
    log_info "uv version: $uv_version"
    log_success "uv tersedia"

    # Cek curl
    if ! command -v curl &>/dev/null; then
        log_warn "curl tidak ditemukan, install: sudo apt install curl"
    fi
}

# ─── Step 1: Install uv ──────────────────────────────────────────────────────
install_uv() {
    log_info "Installing uv..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        # Tambahkan ke PATH untuk session ini
        export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
        log_success "uv berhasil diinstall"
    else
        log_error "Gagal install uv. Coba manual:"
        log_info "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        log_info "  ATAU: pip install uv"
        exit 1
    fi
}

# ─── Step 2: Buat Virtual Environment ────────────────────────────────────────
create_venv() {
    log_step "Step 1: Membuat Virtual Environment"

    cd "$PROJECT_ROOT"

    if [ -d "$VENV_DIR" ]; then
        log_warn "Virtual environment sudah ada di $VENV_DIR"
        read -p "  Hapus dan buat ulang? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
            log_info "Menghapus venv lama..."
        else
            log_info "Menggunakan venv yang sudah ada"
            return 0
        fi
    fi

    uv venv "$VENV_DIR" --python "$PYTHON_MIN_VERSION"
    log_success "Virtual environment dibuat di $VENV_DIR"
}

# ─── Step 3: Install Dependencies ────────────────────────────────────────────
install_dependencies() {
    log_step "Step 2: Install Dependencies"

    cd "$PROJECT_ROOT"

    log_info "Install dependencies utama..."
    uv pip install --python "$VENV_DIR/bin/python" -e ".[dev]"

    log_success "Dependencies utama terinstall"

    # Optional: binary analysis tools
    read -p "  Install binary analysis tools (pwntools, angr)? [~500MB] (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installing binary analysis tools..."
        uv pip install --python "$VENV_DIR/bin/python" pwntools angr bcrypt==4.0.1
        log_success "Binary analysis tools terinstall"
    fi

    # Optional: mitmproxy
    read -p "  Install mitmproxy? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installing mitmproxy..."
        uv pip install --python "$VENV_DIR/bin/python" "mitmproxy>=9.0.0,<11.0.0"
        log_success "mitmproxy terinstall"
    fi
}

# ─── Step 4: Buat Struktur Tests ─────────────────────────────────────────────
create_test_structure() {
    log_step "Step 3: Membuat Struktur Tests"

    mkdir -p tests scripts

    # __init__.py untuk tests
    [ -f tests/__init__.py ] || touch tests/__init__.py

    log_success "Struktur tests dibuat"
}

# ─── Step 5: Verifikasi Installasi ───────────────────────────────────────────
verify_installation() {
    log_step "Step 4: Verifikasi Installasi"

    cd "$PROJECT_ROOT"
    local python_bin="$VENV_DIR/bin/python"

    # Test import module utama
    log_info "Test import hexstrike package..."
    if "$python_bin" -c "
import hexstrike
import hexstrike.config
import hexstrike.core
import hexstrike.core.colors
import hexstrike.core.cache
import hexstrike.core.telemetry
import hexstrike.core.executor
import hexstrike.core.process_manager
import hexstrike.core.visual_engine
import hexstrike.core.logging
print('✅ Core modules OK')

import hexstrike.intelligence
import hexstrike.intelligence.models
import hexstrike.intelligence.decision_engine
print('✅ Intelligence modules OK')

import hexstrike.error_handling
import hexstrike.error_handling.models
import hexstrike.error_handling.handler
print('✅ Error handling modules OK')

import hexstrike.workflows.bugbounty
print('✅ Workflows modules OK')

print()
print('🎉 Semua module berhasil diimport!')
"; then
        log_success "Semua module berhasil diimport"
    else
        log_error "Ada module yang gagal diimport"
        log_info "Cek error di atas untuk detail"
        return 1
    fi

    # Tampilkan versi package terinstall
    log_info "Package terinstall:"
    "$python_bin" -m pip list --format=columns 2>/dev/null | head -20 || \
        uv pip list --python "$python_bin" 2>/dev/null | head -20
}

# ─── Step 6: Cek Syntax Semua File ───────────────────────────────────────────
check_syntax() {
    log_step "Step 5: Cek Syntax Semua File Python"

    cd "$PROJECT_ROOT"
    local python_bin="$VENV_DIR/bin/python"

    local total=0
    local failed=0

    while IFS= read -r -d '' file; do
        ((total++))
        if ! "$python_bin" -m py_compile "$file" 2>/dev/null; then
            log_error "Syntax error: $file"
            ((failed++))
        fi
    done < <(find hexstrike hexstrike_server.py hexstrike_mcp.py -name "*.py" -print0 2>/dev/null)

    if [ $failed -eq 0 ]; then
        log_success "Semua $total file Python syntax OK"
    else
        log_error "$failed dari $total file memiliki syntax error"
        return 1
    fi
}

# ─── Step 7: Setup Git Hooks (Optional) ──────────────────────────────────────
setup_git_hooks() {
    if [ -d .git ]; then
        log_step "Step 6: Setup Git Hooks"

        cat > .git/hooks/pre-commit << 'HOOK'
#!/usr/bin/env bash
# Pre-commit: cek syntax
echo "🔍 Checking Python syntax..."
find hexstrike -name "*.py" -exec python3 -m py_compile {} \; || exit 1
echo "✅ Syntax check passed"
HOOK
        chmod +x .git/hooks/pre-commit
        log_success "Git pre-commit hook terinstall"
    fi
}

# ─── Step 8: Tampilkan Ringkasan ─────────────────────────────────────────────
show_summary() {
    log_step "Setup Selesai! 🎉"

    echo -e "${CYAN}${BOLD}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║                  ✅ SETUP BERHASIL!                              ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Aktivasi environment:                                           ║
║    source .venv/bin/activate                                     ║
║                                                                  ║
║  ATAU gunakan uv run (tanpa aktivasi manual):                    ║
║    uv run python hexstrike_server.py                             ║
║    uv run python hexstrike_mcp.py                                ║
║                                                                  ║
║  Jalankan tests:                                                 ║
║    ./test_all.sh                                                 ║
║    ATAU: uv run pytest tests/ -v                                 ║
║                                                                  ║
║  Atau gunakan Makefile:                                          ║
║    make server        # Start server                             ║
║    make mcp           # Start MCP client                         ║
║    make test          # Run semua tests                          ║
║    make test-unit     # Run unit tests saja                      ║
║    make test-api      # Run API tests                            ║
║    make test-e2e      # Run E2E tests                            ║
║    make lint          # Run linter                               ║
║    make clean         # Cleanup                                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
    banner
    check_prerequisites
    create_venv
    install_dependencies
    create_test_structure
    verify_installation
    check_syntax
    setup_git_hooks
    show_summary
}

# Jalankan
main "$@"