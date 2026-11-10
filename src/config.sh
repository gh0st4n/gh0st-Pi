# ---------------------------------------------------------------------------
# KONFIGURASI
# Semua nilai bisa diganti lewat environment:
#   sudo env NAMA=nilai sh setup.sh
# Semua akar artefak berat di /opt (SSD) kecuali kamu ubah.
# ---------------------------------------------------------------------------
GH0ST_ROOT="${GH0ST_ROOT:-/opt/gh0st-pi}"
LLAMA_HOME="${LLAMA_HOME:-$GH0ST_ROOT/llama}"
LLAMA_MODELS="${LLAMA_MODELS:-$GH0ST_ROOT/models}"
UV_HOME="${UV_HOME:-$GH0ST_ROOT/uv}"

HEX_DIR="${HEX_DIR:-$GH0ST_ROOT/tools/hexstrike-ai}"
HEX_ENV="${HEX_ENV:-$HEX_DIR/hexstrike-env}"
HEX_CACHE="${HEX_CACHE:-$GH0ST_ROOT/.cache/pip}"
HEX_PORT="${HEX_PORT:-8888}"

WORKSPACE="${WORKSPACE:-$GH0ST_ROOT/workspace}"

SV="${SV:-/etc/sv/llama}"
RN="${RN:-/etc/runit/runsvdir/default}"
SVLOG_DIR="${SVLOG_DIR:-/var/log/llama}"
BIN_DIR="${BIN_DIR:-/usr/local/bin}"

# User sistem khusus utk service llama (tanpa hak root, tanpa login)
LLAMA_USER="${LLAMA_USER:-_llama}"
LLAMA_STATE="${LLAMA_STATE:-/var/lib/llama}"

STATE_FILE="$GH0ST_ROOT/.gh0st-pi-state"

PORT="${GH0ST_PORT:-8080}"
CTX="${GH0ST_CTX:-16384}"
THREADS="${GH0ST_THREADS:-}"          # kosong = otomatis (jumlah core - 2)
THINK_EXPLICIT="${GH0ST_THINKING:+1}"   # 1 jika kamu memberi nilai eksplisit
GH0ST_THINKING="${GH0ST_THINKING:-off}" # off = jawaban cepat (disarankan di CPU); on = mode "berpikir"
GH0ST_AUTOSTART="${GH0ST_AUTOSTART:-0}" # 0 = AI TIDAK nyala otomatis saat boot (hemat RAM 16GB)
READY_TIMEOUT="${GH0ST_READY_TIMEOUT:-180}"

GH0ST_BACKEND="${GH0ST_BACKEND:-cpu}"
case "${GH0ST_NGPU:-}" in
  "")
    case "$GH0ST_BACKEND" in
      cpu|auto) NGPU=0 ;;
      *)        NGPU=99 ;;
    esac
    ;;
  *) NGPU="$GH0ST_NGPU" ;;
esac

# FORCE_BUILD lama tetap dikenali sbg alias
GH0ST_REINSTALL="${GH0ST_REINSTALL:-${FORCE_BUILD:-0}}"
GH0ST_SKIP_INSTALL="${GH0ST_SKIP_INSTALL:-0}"
GH0ST_INSTALL_UV="${GH0ST_INSTALL_UV:-0}"
GH0ST_INSTALL_PI="${GH0ST_INSTALL_PI:-1}"
GH0ST_INSTALL_HEXSTRIKE="${GH0ST_INSTALL_HEXSTRIKE:-1}"

# Sumber unduhan (bisa di-override, mis. utk mirror / tes)
LLAMA_INSTALLER_URL="${LLAMA_INSTALLER_URL:-https://llama.app/install.sh}"
UV_INSTALLER_URL="${UV_INSTALLER_URL:-https://astral.sh/uv/install.sh}"
HF_BASE="${HF_BASE:-https://huggingface.co}"

# HexStrike: dikunci ke commit tertentu (HEAD per 2026-08-03). Kosongkan HEX_REF = ikut HEAD (TIDAK disarankan).
REPO_HEX="${REPO_HEX:-https://github.com/0x4m4/hexstrike-ai.git}"
HEX_REF="${HEX_REF:-d689933ff579d839c676c82b231f8e98326c5f04}"

# Pi (agent coding). Versi dikunci; dipilih yang sudah >14 hari beredar & tanpa install-script.
PI_PKG="${PI_PKG:-@earendil-works/pi-coding-agent}"
PI_VERSION="${PI_VERSION:-1.3.0}"
PI_EXT_LIST="${PI_EXT_LIST:-pi-llama-cpp@0.17.0}"
# Ekstensi tambahan = OPT-IN (belum diaudit kodenya). Contoh:
#   GH0ST_PI_EXT_EXTRA="pi-agent-modes@0.3.0 pi-manage-todo-list@0.4.0"
PI_EXT_EXTRA="${GH0ST_PI_EXT_EXTRA:-}"

# GGUF (repo|filename). Model default DI URUTAN PERTAMA supaya terunduh duluan.
if [ -z "${MODELS_LIST:-}" ]; then
  MODELS_LIST='unsloth/Qwen3-4B-GGUF|Qwen3-4B-Q4_K_M.gguf
unsloth/Qwen3-8B-GGUF|Qwen3-8B-Q4_K_M.gguf
unsloth/Qwen2.5-Coder-7B-Instruct-GGUF|Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
unsloth/Qwen2.5-Coder-3B-Instruct-GGUF|Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf'
fi

DEFAULT_MODEL_FILE="${GH0ST_DEFAULT_MODEL:-Qwen3-4B-Q4_K_M.gguf}"

# Status; diisi saat runtime
HEX_OK=0
LLAMA_SMOKE="belum dites"
PI_STATUS="dilewati"
PI_FAIL=""
LLAMA_BIN=""
LLAMA_HELP=""
LLAMA_VER=""
UV_BIN=""
FAILED=""
DEFAULT_MODEL=""
