install_uv() {
  UV_BIN=""

  if [ "$GH0ST_INSTALL_UV" != "1" ]; then
    info "uv dilewati (minim by default; tak dipakai jalur mana pun). Set GH0ST_INSTALL_UV=1 utk pasang."
    return 0
  fi

  if have uv; then
    UV_BIN=$(command -v uv)
    info "uv sudah ada: $UV_BIN"
    return 0
  fi

  if ! have curl; then
    warn "curl tidak ada; uv dilewati."
    return 0
  fi

  ensure_llama_user
  stage="$LLAMA_STATE/uvstage"
  rm -rf "$stage"
  install -d -o "$LLAMA_USER" -g "$LLAMA_USER" -m 755 "$stage" "$stage/bin"

  info "Install uv (astral.sh) sbg user '$LLAMA_USER' (bukan root) lalu salin ke $UV_HOME/bin (milik root)"

  if ! fetch_script "$UV_INSTALLER_URL" "$stage/install.sh" "${GH0ST_UV_INSTALLER_SHA256:-}"; then
    warn "installer uv gagal diunduh; uv dilewati."
    rm -rf "$stage"
    return 0
  fi
  chown "$LLAMA_USER:$LLAMA_USER" "$stage/install.sh"

  set -- "UV_UNMANAGED_INSTALL=$stage/bin"
  if [ -n "${UV_PRINT_QUIET:-}" ]; then
    set -- "$@" "UV_PRINT_QUIET=$UV_PRINT_QUIET"
  fi
  if [ -n "${UV_GITHUB_TOKEN:-}" ]; then
    set -- "$@" "UV_GITHUB_TOKEN=$UV_GITHUB_TOKEN"
    info "UV_GITHUB_TOKEN di-set (anti rate-limit GitHub fallback)"
  fi
  if [ -n "${UV_DOWNLOAD_URL:-}" ]; then
    set -- "$@" "UV_DOWNLOAD_URL=$UV_DOWNLOAD_URL"
    info "UV_DOWNLOAD_URL di-set (pin artifact ketat)"
  fi
  if [ -n "${UV_INSTALLER_GITHUB_BASE_URL:-}" ]; then
    set -- "$@" "UV_INSTALLER_GITHUB_BASE_URL=$UV_INSTALLER_GITHUB_BASE_URL"
    info "UV_INSTALLER_GITHUB_BASE_URL di-set (pin base release)"
  fi

  if ! run_as "$LLAMA_USER" "$stage" env "$@" sh "$stage/install.sh"; then
    warn "installer uv gagal (lihat output di atas); uv dilewati."
    rm -rf "$stage"
    return 0
  fi

  install -d -m 755 -o root -g root "$UV_HOME" "$UV_HOME/bin"
  for b in uv uvx; do
    if [ -x "$stage/bin/$b" ]; then
      install -m 755 -o root -g root "$stage/bin/$b" "$UV_HOME/bin/$b"
    fi
  done
  rm -rf "$stage"

  if [ ! -x "$UV_HOME/bin/uv" ]; then
    warn "uv terinstall tapi binari tak ketemu; uv dilewati."
    return 0
  fi
  UV_BIN="$UV_HOME/bin/uv"

  mkdir -p "$BIN_DIR"
  for b in uv uvx; do
    if [ -x "$UV_HOME/bin/$b" ] && [ ! -e "$BIN_DIR/$b" ]; then
      ln -sf "$UV_HOME/bin/$b" "$BIN_DIR/$b"
    fi
  done

  info "uv -> $UV_BIN (symlink global di $BIN_DIR; rc user TIDAK disentuh; tanpa updater)"
  return 0
}
