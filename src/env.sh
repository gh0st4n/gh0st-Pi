append_once() {
  f="$1"
  marker="$2"
  block="$3"

  if [ ! -f "$f" ]; then
    touch "$f"
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
  if [ -z "$REAL_HOME" ]; then
    warn "no REAL_HOME; skip rc"
    return 0
  fi

  env_bash=$(printf 'export LLAMA_MODELS=%s\nexport LLAMA_SERVER_URL=http://127.0.0.1:%s\n' "$LLAMA_MODELS" "$PORT")
  env_fish=$(printf 'set -gx LLAMA_MODELS %s\nset -gx LLAMA_SERVER_URL http://127.0.0.1:%s\n' "$LLAMA_MODELS" "$PORT")

  if [ -f "$REAL_HOME/.bashrc" ]; then
    append_once "$REAL_HOME/.bashrc" "gh0st-pi-llama-env" "$env_bash"
  fi

  if [ -f "$REAL_HOME/.zshrc" ]; then
    append_once "$REAL_HOME/.zshrc" "gh0st-pi-llama-env" "$env_bash"
  fi

  if [ -d "$REAL_HOME/.config/fish" ]; then
    mkdir -p "$REAL_HOME/.config/fish"
    append_once "$REAL_HOME/.config/fish/config.fish" "gh0st-pi-llama-env" "$env_fish"
  fi

  chown "$REAL_USER" "$REAL_HOME/.bashrc" "$REAL_HOME/.zshrc" 2>/dev/null || true
}