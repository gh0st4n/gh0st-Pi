install_hexstrike() {
  HEX_OK=0
  mkdir -p "$GH0ST_ROOT/tools"

  # (1) clone / update
  if [ ! -d "$HEX_DIR/.git" ]; then
    info "Clone HexStrike AI -> $HEX_DIR"
    if ! git clone --depth 1 "$REPO_HEX" "$HEX_DIR"; then
      warn "clone HexStrike gagal (cek URL/akses/jaringan); pilar [4] dilewati."
      return 0
    fi
  else
    info "HexStrike ada; pull"
    git -C "$HEX_DIR" pull --ff-only 2>/dev/null || warn "pull HexStrike gagal; pakai tree ada"
  fi

  # (2) guard requirements
  if [ ! -f "$HEX_DIR/requirements.txt" ]; then
    warn "requirements.txt tak ditemukan di $HEX_DIR (struktur repo berubah?); pilar [4] dilewati."
    return 0
  fi

  # (3) buat venv
  if ! python3 -m venv "$HEX_ENV"; then
    warn "python3 -m venv gagal (venv-support python3?); pilar [4] dilewati."
    return 0
  fi

  # (4) guard pip-dalam-venv
  if [ ! -x "$HEX_ENV/bin/pip" ]; then
    info "pip belum ada di venv; coba ensurepip --upgrade"
    "$HEX_ENV/bin/python" -m ensurepip --upgrade >/dev/null 2>&1 || true
  fi

  if [ ! -x "$HEX_ENV/bin/pip" ]; then
    warn "pip tak tersedia di venv (ensurepip gagal); pilar [4] dilewati."
    warn "Pada Void pastikan python3 lengkap (ensurepip bundled); lihat [E]."
    return 0
  fi

  # (5) install deps
  mkdir -p "$HEX_CACHE"

  if ! PIP_CACHE_DIR="$HEX_CACHE" "$HEX_ENV/bin/pip" install --upgrade pip >/dev/null 2>&1; then
    warn "pip upgrade gagal (jaringan?); lanjut coba install requirements"
  fi

  if ! PIP_CACHE_DIR="$HEX_CACHE" "$HEX_ENV/bin/pip" install -r "$HEX_DIR/requirements.txt"; then
    warn "pip install -r requirements.txt GAGAL. Sering krn build C-extension butuh"
    warn "python3-devel/gcc/libffi (TIDK di-auto-install; minim by default) -> lihat [E]."
    warn "Pilar [4] ditandai belum siap; venv tetap ada, ulangi manual setelah deps build."
    return 0
  fi

  HEX_OK=1
  info "HexStrike AI siap (venv: $HEX_ENV). Start on-demand: lihat [E]. Port default $HEX_PORT."
}