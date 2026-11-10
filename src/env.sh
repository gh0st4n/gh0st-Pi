ENV_TOUCHED=""

append_once() {
  f="$1"
  marker="$2"
  block="$3"

  if [ ! -f "$f" ]; then
    touch "$f"
    ENV_TOUCHED="$ENV_TOUCHED $f"
  fi

  if grep -q "$marker" "$f" 2>/dev/null; then
    info "env sudah ada di $f, skip"
  else
    cp -a "$f" "$f.gh0stbak.$(date +%s)" 2>/dev/null || true
    printf '\n# %s\n%s\n' "$marker" "$block" >> "$f"
    info "append env gh0st-pi ke $f"
  fi
}

setup_env() {
  if [ -z "$REAL_HOME" ] || [ "$REAL_USER" = root ]; then
    warn "tidak ada user biasa (REAL_USER='${REAL_USER:-}'); lewati penulisan env shell"
    return 0
  fi

  # PI_TELEMETRY=0: matikan ping versi anonim Pi ke pi.dev (privasi utk kerja RE/malware)
  env_bash=$(printf 'export LLAMA_MODELS=%s\nexport LLAMA_SERVER_URL=http://127.0.0.1:%s\nexport PI_TELEMETRY=0\n' "$LLAMA_MODELS" "$PORT")
  env_fish=$(printf 'set -gx LLAMA_MODELS %s\nset -gx LLAMA_SERVER_URL http://127.0.0.1:%s\nset -gx PI_TELEMETRY 0\n' "$LLAMA_MODELS" "$PORT")

  if [ -f "$REAL_HOME/.bashrc" ]; then
    append_once "$REAL_HOME/.bashrc" "gh0st-pi-llama-env" "$env_bash"
  fi

  if [ -f "$REAL_HOME/.zshrc" ]; then
    append_once "$REAL_HOME/.zshrc" "gh0st-pi-llama-env" "$env_bash"
  fi

  if [ -d "$REAL_HOME/.config/fish" ]; then
    append_once "$REAL_HOME/.config/fish/config.fish" "gh0st-pi-llama-env" "$env_fish"
  fi

  # File yg DIBUAT oleh skrip ini (bukan yg sudah ada) harus milik user, bukan root
  _grp=$(id -gn "$REAL_USER" 2>/dev/null || echo "$REAL_USER")
  for f in $ENV_TOUCHED; do
    chown "$REAL_USER:$_grp" "$f" 2>/dev/null || true
  done
  return 0
}
