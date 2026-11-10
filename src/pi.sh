# ---------------------------------------------------------------------------
# Pi (agent coding di terminal) + ekstensi.
# Dipasang SEBAGAI USER BIASA (bukan root) ke ~/.local, versi dikunci.
# Paket yang aktif: @earendil-works/pi-coding-agent (paket lama @mariozechner/... sudah deprecated).
# ---------------------------------------------------------------------------

find_user_pi() {
  for _c in "$REAL_HOME/.local/bin/pi" "$REAL_HOME/.npm-global/bin/pi" "$BIN_DIR/pi"; do
    if [ -x "$_c" ]; then
      printf '%s' "$_c"
      return 0
    fi
  done
  return 1
}

# run_pi ARG... -> jalankan 'pi' sbg user, tanpa stdin (tak bisa menggantung menunggu input)
run_pi() {
  if have timeout; then
    run_as "$REAL_USER" "$REAL_HOME" env PATH="$PI_BINDIR:$PATH" PI_TELEMETRY=0 \
      timeout 300 "$PI_BIN" "$@" < /dev/null
  else
    run_as "$REAL_USER" "$REAL_HOME" env PATH="$PI_BINDIR:$PATH" PI_TELEMETRY=0 \
      "$PI_BIN" "$@" < /dev/null
  fi
}

install_pi() {
  PI_STATUS="dilewati"
  PI_FAIL=""

  if [ "$GH0ST_INSTALL_PI" != 1 ]; then
    info "Pi dilewati (GH0ST_INSTALL_PI=0)"
    return 0
  fi

  if [ -z "$REAL_HOME" ] || [ "$REAL_USER" = root ]; then
    warn "tidak ada user biasa; Pi dilewati. Jalankan setup lewat 'sudo' dari akun biasa, bukan login root."
    PI_STATUS="dilewati (tidak ada user biasa)"
    return 0
  fi

  PI_BIN=$(find_user_pi || true)

  if [ -z "$PI_BIN" ]; then
    if ! have npm; then
      warn "npm tidak ada; Pi tidak bisa dipasang. Pasang nodejs lengkap lalu ulangi."
      PI_STATUS="BELUM (npm tidak ada)"
      return 0
    fi

    _nv=$(node -v 2>/dev/null | sed 's/^v//')
    if ! pi_node_ok "$_nv"; then
      warn "Node '$_nv' terlalu tua utk Pi (butuh >=22.19); Pi dilewati."
      PI_STATUS="BELUM (Node terlalu tua)"
      return 0
    fi

    info "Pasang Pi ($PI_PKG@$PI_VERSION) sbg user '$REAL_USER' ke $REAL_HOME/.local (bukan root)"
    run_as "$REAL_USER" "$REAL_HOME" mkdir -p "$REAL_HOME/.local"
    if ! run_as "$REAL_USER" "$REAL_HOME" npm install -g --prefix "$REAL_HOME/.local" "$PI_PKG@$PI_VERSION" < /dev/null; then
      warn "npm install Pi gagal (jaringan?). Manual sbg user: npm install -g --prefix ~/.local $PI_PKG@$PI_VERSION"
      PI_STATUS="GAGAL (npm install)"
      return 0
    fi

    PI_BIN="$REAL_HOME/.local/bin/pi"
    if [ ! -x "$PI_BIN" ]; then
      warn "npm selesai tapi $PI_BIN tidak ada."
      PI_STATUS="GAGAL (binari tidak ditemukan)"
      return 0
    fi

    # symlink global supaya 'pi' ketemu tanpa mengubah PATH / rc shell
    mkdir -p "$BIN_DIR"
    if [ ! -e "$BIN_DIR/pi" ] || [ -L "$BIN_DIR/pi" ]; then
      ln -sf "$PI_BIN" "$BIN_DIR/pi"
    fi
  else
    info "Pi sudah ada: $PI_BIN (tidak dipasang ulang)"
  fi

  PI_BINDIR=$(dirname "$PI_BIN")
  _piver=$(run_as "$REAL_USER" "$REAL_HOME" env PATH="$PI_BINDIR:$PATH" PI_OFFLINE=1 PI_TELEMETRY=0 "$PI_BIN" --version < /dev/null 2>/dev/null | head -n1 || true)
  PI_STATUS="terpasang (${_piver:-versi tak terbaca})"

  for ext in $PI_EXT_LIST $PI_EXT_EXTRA; do
    if run_pi install "npm:$ext"; then
      info "pi ext OK: $ext"
    else
      warn "pi install npm:$ext gagal; ulangi manual sbg user: pi install npm:$ext"
      PI_FAIL="$PI_FAIL $ext"
    fi
  done

  if [ -n "$PI_FAIL" ]; then
    warn "Ekstensi Pi GAGAL (ulangi manual):$PI_FAIL"
    PI_STATUS="$PI_STATUS; ekstensi gagal:$PI_FAIL"
  fi
  return 0
}
