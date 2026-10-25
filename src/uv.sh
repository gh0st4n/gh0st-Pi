install_uv() {
  if [ "$GH0ST_INSTALL_UV" != "1" ]; then
    info "uv dilewati (minim by default; tak dipakai jalur mana pun). Set GH0ST_INSTALL_UV=1 utk pasang."
    UV_BIN=""
    return 0
  fi

  if have uv; then
    UV_BIN=$(command -v uv)
    info "uv sudah ada: $UV_BIN"
    return 0
  fi

  if ! have curl && ! have wget; then
    err "perlu curl atau wget utk install uv"
  fi

  mkdir -p "$UV_HOME/bin"
  info "Install uv (astral.sh) UNMANAGED -> $UV_HOME/bin (SSD; no rc, no updater)"

  (
    export UV_UNMANAGED_INSTALL="$UV_HOME/bin"

    if [ -n "${UV_PRINT_QUIET:-}" ]; then
      export UV_PRINT_QUIET
    fi

    if [ -n "${UV_GITHUB_TOKEN:-}" ]; then
      export UV_GITHUB_TOKEN
      info "UV_GITHUB_TOKEN di-set (anti rate-limit GitHub fallback)"
    fi

    if [ -n "${UV_DOWNLOAD_URL:-}" ]; then
      export UV_DOWNLOAD_URL
      info "UV_DOWNLOAD_URL di-set (pin artifact ketat)"
    fi

    if [ -n "${UV_INSTALLER_GITHUB_BASE_URL:-}" ]; then
      export UV_INSTALLER_GITHUB_BASE_URL
      info "UV_INSTALLER_GITHUB_BASE_URL di-set (pin base release)"
    fi

    if have curl; then
      curl -LsSf https://astral.sh/uv/install.sh | sh
    else
      wget -qO- https://astral.sh/uv/install.sh | sh
    fi
  ) || err "installer uv gagal (lihat output di atas)"

  UV_BIN="$UV_HOME/bin/uv"

  if [ ! -x "$UV_BIN" ]; then
    for c in "$UV_HOME/bin/uv" "$UV_HOME/uv"; do
      if [ -x "$c" ]; then
        UV_BIN="$c"
        break
      fi
    done
  fi

  if [ ! -x "$UV_BIN" ]; then
    err "uv terinstall tapi binari tak ketemu di $UV_HOME/bin"
  fi

  for b in uv uvx; do
    s=$(dirname "$UV_BIN")/$b
    if [ -x "$s" ] && [ ! -e "/usr/local/bin/$b" ]; then
      ln -sf "$s" "/usr/local/bin/$b"
    fi
  done

  if have uv; then
    UV_BIN=$(command -v uv)
  fi

  info "uv -> $UV_BIN (symlink global /usr/local/bin; rc user TIDAK disentuh; tanpa updater)"
}