#!/bin/sh
# Install Ollama to Root Partition (/opt/ollama) & set up a Runit service.
#
# Security model (same as setup.sh for llama):
#   - The server runs as a dedicated system user '_ollama' (NOT root).
#   - /opt/ollama (binary, libs) stays owned by root; only the models dir belongs to '_ollama'.
#   - Archive is downloaded to a file, its sha256 is logged and can be pinned.

set -e

err() { printf '%s: %s\n' "$0" "$*" >&2; exit 1; }
info() { printf '%s: %s\n' "$0" "$*" >&2; }

root() {
  [ "$(id -u)" -eq 0 ] || err "This script requires root, run with sudo"
}

PATH_OLLAMA="${PATH_OLLAMA:-/opt/ollama}"
MODEL_OLLAMA="${MODEL_OLLAMA:-$PATH_OLLAMA/models}"
URL="${OLLAMA_URL:-https://ollama.com/download/ollama-linux-amd64.tar.zst}"
OUTPUT="${OLLAMA_TMP:-/tmp/ollama-linux-amd64.tar.zst}"

SV="${SV:-/etc/sv/ollama}"
RN="${RN:-/etc/runit/runsvdir/default}"
SVLOG_DIR="${SVLOG_DIR:-/var/log/ollama}"
BIN_DIR="${BIN_DIR:-/usr/local/bin}"
OLLAMA_USER="${OLLAMA_USER:-_ollama}"
OLLAMA_STATE="${OLLAMA_STATE:-/var/lib/ollama}"
OLLAMA_PORT="${OLLAMA_PORT:-11434}"

MODELS="${OLLAMA_MODELS_LIST:-qwen2.5-coder:7b qwen2.5-coder:3b qwen3:8b qwen3:4b}"

root

command -v chpst >/dev/null 2>&1 || err "'chpst' (runit) not found"
command -v useradd >/dev/null 2>&1 || err "'useradd' (shadow) not found"

if ! id "$OLLAMA_USER" >/dev/null 2>&1; then
  info "Creating system user '$OLLAMA_USER' (the server will NOT run as root)"
  _nologin=$(command -v nologin 2>/dev/null || echo /bin/false)
  useradd --system --user-group --no-create-home --home-dir "$OLLAMA_STATE" \
    --shell "$_nologin" "$OLLAMA_USER" || err "could not create user $OLLAMA_USER"
fi
install -d -o "$OLLAMA_USER" -g "$OLLAMA_USER" -m 750 "$OLLAMA_STATE"

info "Creating Directories : $PATH_OLLAMA, $MODEL_OLLAMA"
install -d -m 755 -o root -g root "$PATH_OLLAMA"
install -d -m 755 -o "$OLLAMA_USER" -g "$OLLAMA_USER" "$MODEL_OLLAMA"

info "Downloading Ollama from $URL"
# -f: fail on HTTP errors instead of saving an error page as the archive
curl -fL --retry 3 --connect-timeout 20 "$URL" -o "$OUTPUT" || err "download failed: $URL"
_hash=$(sha256sum "$OUTPUT" | cut -d' ' -f1)
info "archive sha256=$_hash"
if [ -n "${OLLAMA_SHA256:-}" ] && [ "$OLLAMA_SHA256" != "$_hash" ]; then
  rm -f "$OUTPUT"
  err "sha256 mismatch (expected $OLLAMA_SHA256)"
fi

info "Extraction to $PATH_OLLAMA"
if tar --help 2>&1 | grep -q -- '--zstd'; then
  tar --zstd -C "$PATH_OLLAMA" -xf "$OUTPUT"
elif command -v zstd > /dev/null 2>&1; then
  zstd -d -c "$OUTPUT" | tar -C "$PATH_OLLAMA" -xf -
else
  err "Need 'tar --zstd' support or 'zstd' binary installed to extract this archive. Install zstd (e.g. xbps-install -S zstd) and re-run"
fi

rm -f "$OUTPUT"

# Extracted files must be root-owned (never writable by the service user or a normal user)
chown -R root:root "$PATH_OLLAMA"
chown "$OLLAMA_USER:$OLLAMA_USER" "$MODEL_OLLAMA"

ENV_BLOCK_BASH="
export PATH=$PATH_OLLAMA/bin:\$PATH
export LD_LIBRARY_PATH=$PATH_OLLAMA/lib/ollama:\$LD_LIBRARY_PATH
export OLLAMA_MODELS=$MODEL_OLLAMA
"

ENV_BLOCK_FISH="
set -gx PATH $PATH_OLLAMA/bin \$PATH
set -gx LD_LIBRARY_PATH $PATH_OLLAMA/lib/ollama \$LD_LIBRARY_PATH
set -gx OLLAMA_MODELS $MODEL_OLLAMA
"

REAL_USER="${SUDO_USER:-${DOAS_USER:-${USER:-}}}"
REAL_HOME=""
if [ -n "$REAL_USER" ]; then
  REAL_HOME=$(getent passwd "$REAL_USER" | cut -d: -f6)
fi

append_once() {
  file="$1"; marker="$2"; block="$3"
  [ -f "$file" ] || touch "$file"
  if grep -q "$marker" "$file" 2>/dev/null; then
    info "Env already present in $file, skipping"
  else
    printf '\n# %s\n%s\n' "$marker" "$block" >> "$file"
    info "Appended ollama env to $file"
  fi
}

if [ -n "$REAL_HOME" ] && [ "$REAL_USER" != root ]; then
  [ -f "$REAL_HOME/.bashrc" ] && append_once "$REAL_HOME/.bashrc" "ollama-env" "$ENV_BLOCK_BASH"
  [ -f "$REAL_HOME/.zshrc" ] && append_once "$REAL_HOME/.zshrc" "ollama-env" "$ENV_BLOCK_BASH"
  if [ -d "$REAL_HOME/.config/fish" ]; then
    _fishnew=0
    [ -f "$REAL_HOME/.config/fish/config.fish" ] || _fishnew=1
    append_once "$REAL_HOME/.config/fish/config.fish" "ollama-env" "$ENV_BLOCK_FISH"
    if [ "$_fishnew" = 1 ]; then
      chown "$REAL_USER:$(id -gn "$REAL_USER")" "$REAL_HOME/.config/fish/config.fish" 2>/dev/null || true
    fi
  fi
else
  info "No regular user home found (REAL_USER='${REAL_USER:-}'), skipping shell rc setup"
fi

info "Setting up runit service at $SV"
mkdir -p "$SV/log" "$SVLOG_DIR"
chmod 750 "$SVLOG_DIR"

cat > "$SV/run" << EOF
#!/bin/sh
exec 2>&1
exec chpst -u $OLLAMA_USER env \\
  HOME=$OLLAMA_STATE \\
  PATH=$PATH_OLLAMA/bin:/usr/bin:/bin \\
  LD_LIBRARY_PATH=$PATH_OLLAMA/lib/ollama \\
  OLLAMA_MODELS=$MODEL_OLLAMA \\
  $PATH_OLLAMA/bin/ollama serve
EOF
chmod +x "$SV/run"

printf '#!/bin/sh\nexec svlogd -tt %s\n' "$SVLOG_DIR" > "$SV/log/run"
chmod +x "$SV/log/run"

if [ -L "$RN/ollama" ] || [ -e "$RN/ollama" ]; then
  info "Service already linked at $RN/ollama, skipping"
else
  ln -s "$SV" "$RN/ollama"
  info "Linked $SV -> $RN/ollama"
fi

info "Waiting for runsvdir to pick up the new service (polling, no global signal)"

tries=0
while [ ! -e "$RN/ollama/supervise/ok" ]; do
  tries=$((tries + 1))
  if [ "$tries" -ge 15 ]; then
    info "runsvdir still hasn't picked up the service after 15s, trying anyway"
    break
  fi
  sleep 1
done

info "Starting Ollama service via runit"
sv up "$SV" > /dev/null 2>&1 || true

info "Waiting for Ollama service to come up..."
tries=0
until curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$OLLAMA_PORT" 2>/dev/null | grep -q '^200$'; do
  tries=$((tries + 1))   # (the original never incremented this => infinite loop)
  if [ "$tries" -ge 30 ]; then
    err "Ollama service did not become ready in time. Check 'tail $SVLOG_DIR/current' and 'sudo sv status $SV'."
  fi
  sleep 1
done
info "Ollama service is up (http://127.0.0.1:$OLLAMA_PORT)"

info "Giving DNS/Network a moment to settle before pulling models"
sleep "${OLLAMA_SETTLE:-5}"

info "Pulling Models: $MODELS"
for model in $MODELS; do
  info "Pulling $model (this can take a while depending on model size and connection)"
  pull_tries=0
  until OLLAMA_HOST="127.0.0.1:$OLLAMA_PORT" "$PATH_OLLAMA/bin/ollama" pull "$model"; do
    pull_tries=$((pull_tries + 1))
    if [ "$pull_tries" -ge 3 ]; then
      err "Failed to pull $model after 3 attempts. Check your internet connection and run manually: 'ollama pull $model'"
    fi
    info "Pull failed, retrying in 10s ($pull_tries/3)..."
    sleep 10
  done
done

if [ -n "$REAL_HOME" ]; then
  shell_rc=""
  [ -f "$REAL_HOME/.bashrc" ] && shell_rc="$REAL_HOME/.bashrc"
  [ -f "$REAL_HOME/.zshrc" ] && shell_rc="$REAL_HOME/.zshrc"
  [ -f "$REAL_HOME/.config/fish/config.fish" ] && shell_rc="$REAL_HOME/.config/fish/config.fish"
fi

info "Done"
info "Binary     : $PATH_OLLAMA/bin/ollama  (root-owned)"
info "Models dir : $MODEL_OLLAMA  (owned by $OLLAMA_USER)"
info "Service    : sudo sv status $SV   | logs: tail -f $SVLOG_DIR/current"
info "Restart your shell (or run: source ${shell_rc:-~/.bashrc}) to pick up the new PATH"
info "Usage:"
info "  ollama run qwen2.5-coder:7b # Coding/Assistant"
info "  ollama run qwen3:8b         # Security/CTF"
