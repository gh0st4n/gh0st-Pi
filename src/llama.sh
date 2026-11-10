# ---------------------------------------------------------------------------
# llama (mesin penjalan model AI lokal)
#
# Desain keamanan:
#  - Installer resmi diunduh ke FILE (hash dicatat), BUKAN 'curl | sh' sebagai root.
#  - Installer dijalankan sbg user sistem '_llama' (tanpa hak root) di folder sementara.
#  - Binari hasilnya (statis, 1 file) DISALIN ke $LLAMA_HOME/bin/llama, milik root.
#    Jadi service tidak bisa menimpa binarinya sendiri, dan user biasa pun tidak.
# ---------------------------------------------------------------------------

ensure_llama_user() {
  if ! id "$LLAMA_USER" >/dev/null 2>&1; then
    info "Buat user sistem '$LLAMA_USER' (service AI jalan tanpa hak root)"
    _nologin=$(command -v nologin 2>/dev/null || echo /bin/false)
    if ! useradd --system --user-group --no-create-home \
         --home-dir "$LLAMA_STATE" --shell "$_nologin" "$LLAMA_USER"; then
      err "gagal membuat user '$LLAMA_USER'"
    fi
  fi

  install -d -o "$LLAMA_USER" -g "$LLAMA_USER" -m 750 "$LLAMA_STATE"
}

link_llama() {
  mkdir -p "$BIN_DIR"
  if ! ln -sf "$LLAMA_BIN" "$BIN_DIR/llama"; then
    warn "gagal symlink $BIN_DIR/llama"
  fi
}

llama_has_flag() {
  printf '%s\n' "$LLAMA_HELP" | grep -Eq -- "$1"
}

# Baca --help server SEKALI (sbg user biasa) lalu putuskan flag mana yang aman dipakai.
# Flag opsional hanya dipakai jika benar-benar disebut di help versi yang terpasang.
llama_probe_flags() {
  LLAMA_VER=$(run_as "$LLAMA_USER" "$LLAMA_STATE" "$LLAMA_BIN" version 2>/dev/null | head -n1)
  LLAMA_HELP=$(run_as "$LLAMA_USER" "$LLAMA_STATE" "$LLAMA_BIN" serve --help 2>&1 || true)

  HAS_JINJA=0
  HAS_REASONING=0
  HAS_THREADS=0
  HAS_NGL=0

  if [ -z "$LLAMA_HELP" ]; then
    warn "'llama serve --help' kosong; memakai flag inti saja (--model --host --port --ctx-size --parallel)."
    return 0
  fi

  if ! llama_has_flag '--model'; then
    warn "'llama serve --help' tak menyebut '--model'; flag server mungkin beda versi."
    warn "Jika service gagal: lihat $SVLOG_DIR/current dan README bagian Troubleshooting."
  fi

  if llama_has_flag '--jinja'; then HAS_JINJA=1; fi
  if llama_has_flag '--reasoning([[:space:]]|\[|<|,|=)'; then HAS_REASONING=1; fi
  if llama_has_flag '--threads'; then HAS_THREADS=1; fi
  if llama_has_flag '--n-gpu-layers'; then HAS_NGL=1; fi
  return 0
}

# Hasil: EXTRA_FLAGS (selalu dipakai) + HAS_REASONING (dipakai bila THINK=off)
build_llama_flags() {
  EXTRA_FLAGS=""

  if [ "${HAS_JINJA:-0}" = 1 ]; then
    EXTRA_FLAGS="$EXTRA_FLAGS --jinja"
  fi

  if [ "${HAS_THREADS:-0}" = 1 ]; then
    _t="$THREADS"
    if [ -z "$_t" ]; then
      _n=$(nproc 2>/dev/null || echo 4)
      if [ "$_n" -ge 4 ]; then
        _t=$((_n - 2))
      else
        _t=$_n
      fi
    fi
    EXTRA_FLAGS="$EXTRA_FLAGS --threads $_t"
  fi

  if [ "$NGPU" != 0 ] && [ "${HAS_NGL:-0}" = 1 ]; then
    EXTRA_FLAGS="$EXTRA_FLAGS --n-gpu-layers $NGPU"
  fi

  EXTRA_FLAGS=${EXTRA_FLAGS# }
  return 0
}

install_official_llama() {
  LLAMA_BIN="$LLAMA_HOME/bin/llama"
  ensure_llama_user

  if [ -x "$LLAMA_BIN" ] && [ "$GH0ST_REINSTALL" != "1" ]; then
    info "binari llama sudah ada (skip). GH0ST_REINSTALL=1 untuk pasang ulang."
    link_llama
    llama_probe_flags
    return 0
  fi

  need curl

  case "$GH0ST_BACKEND" in
    cpu)
      BK="SKIP_CUDA=1 SKIP_ROCM=1 SKIP_VULKAN=1"
      ;;
    cuda)
      BK="SKIP_ROCM=1 SKIP_VULKAN=1"
      ;;
    rocm)
      BK="SKIP_CUDA=1 SKIP_VULKAN=1"
      ;;
    vulkan)
      BK="SKIP_CUDA=1 SKIP_ROCM=1"
      ;;
    auto)
      BK=""
      ;;
    *)
      warn "GH0ST_BACKEND='$GH0ST_BACKEND' tak dikenal; fallback cpu"
      BK="SKIP_CUDA=1 SKIP_ROCM=1 SKIP_VULKAN=1"
      ;;
  esac

  SI=""
  if [ "$GH0ST_SKIP_INSTALL" = "1" ]; then
    SI="SKIP_INSTALL=1"
  fi

  stage="$LLAMA_STATE/stage"
  rm -rf "$stage"
  install -d -o "$LLAMA_USER" -g "$LLAMA_USER" -m 755 "$stage"

  if ! fetch_script "$LLAMA_INSTALLER_URL" "$stage/install.sh" "${GH0ST_LLAMA_INSTALLER_SHA256:-}"; then
    err "tidak bisa mengunduh installer llama. Cek koneksi."
  fi
  chown "$LLAMA_USER:$LLAMA_USER" "$stage/install.sh"

  if [ -z "${GH0ST_LLAMA_INSTALLER_SHA256:-}" ]; then
    info "(installer tidak dikunci hash; hash di atas tercatat. Isi GH0ST_LLAMA_INSTALLER_SHA256 utk mengunci.)"
  fi

  # shellcheck disable=SC2086  # BK/SI = daftar VAR=nilai, dipisah kata disengaja
  set -- $BK $SI
  if [ -n "${HF_TOKEN:-}" ]; then
    set -- "$@" "HF_TOKEN=$HF_TOKEN"
    info "HF_TOKEN di-set (auth bucket / anti rate-limit)"
  fi
  if [ -n "${LLAMA_VERSION:-}" ]; then
    set -- "$@" "LLAMA_VERSION=$LLAMA_VERSION"
    info "pin LLAMA_VERSION=$LLAMA_VERSION"
  fi
  if [ -n "${LLAMA_BUCKET:-}" ]; then
    set -- "$@" "LLAMA_BUCKET=$LLAMA_BUCKET"
    info "override LLAMA_BUCKET=$LLAMA_BUCKET"
  fi

  info "Jalankan installer llama sbg user '$LLAMA_USER' (bukan root), backend=$GH0ST_BACKEND"
  if ! run_as "$LLAMA_USER" "$stage" env "$@" sh "$stage/install.sh"; then
    err "installer resmi GAGAL. Cek output/koneksi/HF bucket; pin LLAMA_VERSION bila perlu."
  fi

  src=""
  for c in "$stage/.llama-app/llama" "$stage/.local/bin/llama"; do
    if [ -s "$c" ]; then
      src="$c"
      break
    fi
  done

  if [ -z "$src" ]; then
    err "binari llama tak ditemukan pasca-install di $stage"
  fi

  # Installer resmi punya bug yg bisa menghasilkan binari 0 byte tanpa error (terutama tanpa zstd).
  size=$(wc -c < "$src" | tr -d ' ')
  if [ "$size" -lt 1000000 ]; then
    err "binari llama hanya $size byte (rusak). Pasang zstd lalu ulangi: sudo xbps-install -S zstd"
  fi

  ver=$(run_as "$LLAMA_USER" "$stage" "$src" version 2>/dev/null | head -n1)
  if [ -z "$ver" ]; then
    err "binari tak bisa dieksekusi / 'version' kosong: $src"
  fi

  install -d -m 755 -o root -g root "$LLAMA_HOME" "$LLAMA_HOME/bin"
  install -m 755 -o root -g root "$src" "$LLAMA_BIN"
  rm -rf "$stage"

  info "llama terpasang: $ver"
  _build=$(printf '%s' "$ver" | sed -n 's/.*build \([0-9][0-9]*\).*/\1/p')
  if [ -n "$_build" ] && [ -z "${LLAMA_VERSION:-}" ]; then
    info "installer ini memasang build NIGHTLY terbaru. Utk hasil yg sama di lain waktu: LLAMA_VERSION=b$_build"
  fi

  if [ -n "$SI" ] && [ -n "${LLAMA_VERSION:-}" ]; then
    warn "SKIP_INSTALL + LLAMA_VERSION di-set: upstream TIDAK verifikasi pin. Yakin '$ver' = $LLAMA_VERSION?"
  fi

  link_llama
  info "symlink global: $BIN_DIR/llama -> $LLAMA_BIN"
  llama_probe_flags
  return 0
}
