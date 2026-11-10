# ---------------------------------------------------------------------------
# HexStrike AI (server MCP utk tool keamanan). On-demand, BUKAN service runit.
#
# Aturan keamanan di sini:
#  - Semua (git, venv, pip) jalan sbg user biasa, TIDAK sbg root.
#  - Source dikunci ke commit $HEX_REF (bukan HEAD yang berubah-ubah).
#  - Upstream menjalankan app.run(host="0.0.0.0") dan /api/command mengeksekusi perintah
#    shell TANPA autentikasi => siapa pun di jaringan yg sama bisa menjalankan perintah.
#    Karena itu dipasang peluncur 'gh0st-hexstrike' yang memaksa bind 127.0.0.1.
# ---------------------------------------------------------------------------

hex_git() {
  run_as "$REAL_USER" "$REAL_HOME" git -C "$HEX_DIR" "$@"
}

hex_pip() {
  run_as "$REAL_USER" "$REAL_HOME" env PIP_CACHE_DIR="$HEX_CACHE" "$HEX_ENV/bin/pip" "$@"
}

install_hexstrike() {
  HEX_OK=0

  if [ "$GH0ST_INSTALL_HEXSTRIKE" != 1 ]; then
    info "HexStrike dilewati (GH0ST_INSTALL_HEXSTRIKE=0)"
    return 0
  fi

  if [ -z "$REAL_HOME" ] || [ "$REAL_USER" = root ]; then
    warn "tidak ada user biasa; HexStrike dilewati (tidak dipasang sbg root)."
    return 0
  fi

  _grp=$(id -gn "$REAL_USER" 2>/dev/null || echo "$REAL_USER")
  install -d -m 755 "$GH0ST_ROOT/tools"
  install -d -o "$REAL_USER" -g "$_grp" -m 755 "$HEX_DIR" "$HEX_CACHE"

  # (1) ambil source pada commit terkunci
  if [ ! -d "$HEX_DIR/.git" ]; then
    info "Ambil HexStrike AI -> $HEX_DIR (commit ${HEX_REF:-HEAD})"
    if ! hex_git init -q; then
      warn "git init gagal; pilar HexStrike dilewati."
      return 0
    fi
    hex_git remote add origin "$REPO_HEX"
  else
    hex_git remote set-url origin "$REPO_HEX" || true
  fi

  if [ -n "$HEX_REF" ]; then
    if ! hex_git fetch -q --depth 1 origin "$HEX_REF" 2>/dev/null; then
      info "fetch per-SHA tidak didukung; fetch penuh"
      if ! hex_git fetch -q origin; then
        warn "git fetch HexStrike gagal (jaringan/URL); pilar HexStrike dilewati."
        return 0
      fi
    fi
    if ! hex_git checkout -q --detach "$HEX_REF"; then
      warn "checkout $HEX_REF gagal; pilar HexStrike dilewati."
      return 0
    fi
    _head=$(hex_git rev-parse HEAD 2>/dev/null)
    case "$HEX_REF" in
      [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]*)
        case "$_head" in
          "$HEX_REF"*) : ;;
          *)
            warn "HEAD ($_head) != HEX_REF ($HEX_REF); dibatalkan."
            return 0
            ;;
        esac
        ;;
    esac
  else
    warn "HEX_REF kosong: ikut HEAD upstream (TIDAK terkunci)."
    if ! hex_git fetch -q --depth 1 origin HEAD || ! hex_git checkout -q --detach FETCH_HEAD; then
      warn "ambil HEAD HexStrike gagal; pilar HexStrike dilewati."
      return 0
    fi
  fi

  # (2) guard requirements
  if [ ! -f "$HEX_DIR/requirements.txt" ]; then
    warn "requirements.txt tak ditemukan di $HEX_DIR (struktur repo berubah?); pilar HexStrike dilewati."
    return 0
  fi

  # (3) venv (milik user)
  if [ ! -x "$HEX_ENV/bin/python" ]; then
    if ! run_as "$REAL_USER" "$REAL_HOME" python3 -m venv "$HEX_ENV"; then
      warn "python3 -m venv gagal (venv-support python3?); pilar HexStrike dilewati."
      return 0
    fi
  fi

  if [ ! -x "$HEX_ENV/bin/pip" ]; then
    info "pip belum ada di venv; coba ensurepip --upgrade"
    run_as "$REAL_USER" "$REAL_HOME" "$HEX_ENV/bin/python" -m ensurepip --upgrade >/dev/null 2>&1 || true
  fi

  if [ ! -x "$HEX_ENV/bin/pip" ]; then
    warn "pip tak tersedia di venv (ensurepip gagal); pilar HexStrike dilewati."
    return 0
  fi

  # (4) install deps (sekali coba; bila gagal pasang paket build lalu coba sekali lagi)
  if ! hex_pip install --upgrade pip >/dev/null 2>&1; then
    warn "pip upgrade gagal (jaringan?); lanjut coba install requirements"
  fi

  if ! hex_pip install -r "$HEX_DIR/requirements.txt"; then
    warn "pip install gagal. Biasanya butuh compiler/header; memasang python3-devel gcc libffi-devel lalu coba SEKALI lagi."
    xbps_try python3-devel
    xbps_try gcc
    xbps_try libffi-devel
    if ! hex_pip install -r "$HEX_DIR/requirements.txt"; then
      warn "pip install -r requirements.txt tetap GAGAL; pilar HexStrike belum siap."
      warn "Venv tetap ada. Ulangi manual: $HEX_ENV/bin/pip install -r $HEX_DIR/requirements.txt"
      return 0
    fi
  fi

  # (5) peluncur aman (WAJIB; tanpa ini server akan terbuka ke seluruh jaringan)
  _launch_src="$SCRIPT_DIR/bin/hexstrike_local.py"
  _wrap_src="$SCRIPT_DIR/bin/gh0st-hexstrike"
  if [ ! -f "$_launch_src" ] || [ ! -f "$_wrap_src" ]; then
    warn "peluncur aman (bin/hexstrike_local.py, bin/gh0st-hexstrike) tidak ada;"
    warn "HexStrike TIDAK ditandai siap. JANGAN jalankan hexstrike_server.py langsung (bind 0.0.0.0, tanpa auth)."
    return 0
  fi

  install -m 644 -o root -g root "$_launch_src" "$GH0ST_ROOT/tools/hexstrike_local.py"
  _tmp=$(mktemp)
  sed -e "s|@HEX_DIR@|$HEX_DIR|g" \
      -e "s|@HEX_ENV@|$HEX_ENV|g" \
      -e "s|@HEX_PORT@|$HEX_PORT|g" \
      -e "s|@LAUNCHER@|$GH0ST_ROOT/tools/hexstrike_local.py|g" "$_wrap_src" > "$_tmp"
  mkdir -p "$BIN_DIR"
  install -m 755 -o root -g root "$_tmp" "$BIN_DIR/gh0st-hexstrike"
  rm -f "$_tmp"

  HEX_OK=1
  info "HexStrike siap (venv: $HEX_ENV). Jalankan: gh0st-hexstrike  (hanya 127.0.0.1:$HEX_PORT)"
  return 0
}
