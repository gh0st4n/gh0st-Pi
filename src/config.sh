# ---------------------------------------------------------------------------
# KONFIGURASI
# Semua akar artefak berat di /opt (SSD).
# ---------------------------------------------------------------------------
GH0ST_ROOT="/opt/gh0st-pi"
LLAMA_HOME="$GH0ST_ROOT/llama"
LLAMA_MODELS="$GH0ST_ROOT/models"
UV_HOME="$GH0ST_ROOT/uv"

HEX_DIR="$GH0ST_ROOT/tools/hexstrike-ai"
HEX_ENV="$HEX_DIR/hexstrike-env"
HEX_CACHE="$GH0ST_ROOT/.cache/pip"
HEX_PORT=8888

WORKSPACE="$GH0ST_ROOT/workspace"

SV="/etc/sv/llama"
RN="/etc/runit/runsvdir/default"

PORT=8080
CTX=16384
NGPU=0

FORCE_BUILD="${FORCE_BUILD:-0}"
GH0ST_BACKEND="${GH0ST_BACKEND:-cpu}"
GH0ST_SKIP_INSTALL="${GH0ST_SKIP_INSTALL:-0}"
GH0ST_INSTALL_UV="${GH0ST_INSTALL_UV:-0}"

REPO_HEX="https://github.com/0x4m4/hexstrike-ai.git"

PI_EXT_LIST="pi-llama-cpp pi-agent-modes pi-themes pi-manage-todo-list pi-redteam pi-security-analysis"

# GGUF (repo|filename)
MODELS_LIST='unsloth/Qwen2.5-Coder-7B-Instruct-GGUF|Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf
unsloth/Qwen2.5-Coder-3B-Instruct-GGUF|Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf
unsloth/Qwen3-8B-GGUF|Qwen3-8B-Q4_K_M.gguf
unsloth/Qwen3-4B-GGUF|Qwen3-4B-Q4_K_M.gguf'

DEFAULT_MODEL_FILE="Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf"

# Status pilar HexStrike; di-set 1 hanya jika venv + pip sukses
HEX_OK=0

# Global lain yang diisi saat runtime
LLAMA_BIN=""
UV_BIN=""
FAILED=""
DEFAULT_MODEL=""