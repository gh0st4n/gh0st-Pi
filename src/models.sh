# ---------------------------------------------------------------------------
# Unduh model GGUF.
#  - Bisa DILANJUTKAN (curl -C -): koneksi putus tidak mengulang dari nol.
#  - Diverifikasi: header "GGUF" + SHA256 dari Hugging Face (x-linked-etag) bila tersedia.
#  - Model default diunduh PERTAMA.
# ---------------------------------------------------------------------------

gguf_magic_ok() {
  [ "$(head -c 4 "$1" 2>/dev/null)" = "GGUF" ]
}

# SHA256 resmi file LFS dari header HF; kosong jika tidak tersedia.
gguf_expected_sha() {
  # Semua huruf dikecilkan dulu: nama header bisa 'x-linked-etag' / 'X-Linked-ETag' / 'X-Linked-Etag'
  # tergantung server/versi HTTP. (Versi pertama case-sensitive -> SHA tak pernah terbaca.)
  curl -sIL --connect-timeout 20 -m 40 "$1" 2>/dev/null \
    | tr -d '\r' \
    | tr '[:upper:]' '[:lower:]' \
    | sed -n 's/^x-linked-etag: *"\{0,1\}\([0-9a-f]\{64\}\).*$/\1/p' \
    | head -n 1
}

# gguf_accept FILE SHA_DIHARAPKAN -> 0 jika file lengkap & benar
gguf_accept() {
  if [ ! -s "$1" ]; then
    return 1
  fi
  if ! gguf_magic_ok "$1"; then
    warn "bukan file GGUF (header salah): $1"
    return 1
  fi
  if [ -n "$2" ]; then
    _got=$(sha256_of "$1")
    if [ "$_got" != "$2" ]; then
      warn "SHA256 tidak cocok utk $1 (dapat $_got, seharusnya $2)"
      return 1
    fi
  else
    warn "SHA256 resmi tidak tersedia; hanya header GGUF yang dicek: $1"
  fi
  return 0
}

# fetch_gguf URL DEST -> 0 jika sukses
fetch_gguf() {
  _url="$1"
  _dest="$2"
  _part="$_dest.part"
  _expect=$(gguf_expected_sha "$_url")
  _tries=0

  # sisa unduhan yg ternyata bukan GGUF (mis. halaman error HTML) jangan dilanjutkan
  if [ -s "$_part" ] && [ "$(wc -c < "$_part" | tr -d ' ')" -ge 4 ] && ! gguf_magic_ok "$_part"; then
    warn "$_part rusak; mulai dari awal"
    rm -f "$_part"
  fi

  while [ "$_tries" -lt 4 ]; do
    _tries=$((_tries + 1))
    _rc=0
    curl -fL --retry 2 --connect-timeout 20 -C - -o "$_part" "$_url" || _rc=$?

    if [ "$_rc" -eq 0 ]; then
      if gguf_accept "$_part" "$_expect"; then
        mv -f "$_part" "$_dest"
        return 0
      fi
      warn "unduhan selesai tapi tidak lolos verifikasi; ulang dari awal"
      rm -f "$_part"
    else
      warn "putus/gagal (curl rc=$_rc), percobaan $_tries/4; lanjutkan dalam ${GH0ST_RETRY_SLEEP:-10}s (file sebagian DISIMPAN)"
    fi

    sleep "${GH0ST_RETRY_SLEEP:-10}"
  done

  # Kasus: .part sebenarnya sudah lengkap (server menolak resume dgn 416)
  if gguf_accept "$_part" "$_expect"; then
    mv -f "$_part" "$_dest"
    return 0
  fi

  return 1
}

download_models() {
  mkdir -p "$LLAMA_MODELS"
  need curl
  FAILED=""

  info "Unduh GGUF -> $LLAMA_MODELS (model default lebih dulu; bisa dilanjutkan bila putus)"

  _free_kb=$(df -Pk "$LLAMA_MODELS" 2>/dev/null | awk 'NR==2 {print $4}')
  if [ -n "$_free_kb" ] && [ "$_free_kb" -lt 20000000 ] 2>/dev/null; then
    warn "Ruang kosong < 20 GB di $LLAMA_MODELS. Keempat model butuh sekitar 15 GB."
    warn "Hemat: sudo env LLAMA_MODELS=/mnt/hdd/gh0st-models sh setup.sh (atau kurangi MODELS_LIST)."
  fi

  while IFS='|' read -r repo file; do
    if [ -z "$repo" ]; then
      continue
    fi

    dest="$LLAMA_MODELS/$file"

    if [ -s "$dest" ] && gguf_magic_ok "$dest"; then
      info "ada, skip: $file"
      continue
    fi

    info "unduh: $file"
    if ! fetch_gguf "$HF_BASE/$repo/resolve/main/$file" "$dest"; then
      warn "MENYERAH $file (jalankan ulang setup.sh nanti; unduhan yang terputus akan DILANJUTKAN)"
      FAILED="$FAILED $file"
    fi
  done <<EOF
$MODELS_LIST
EOF

  DEFAULT_MODEL="$LLAMA_MODELS/$DEFAULT_MODEL_FILE"

  if [ ! -s "$DEFAULT_MODEL" ]; then
    warn "Model default '$DEFAULT_MODEL_FILE' belum ada -> AI belum bisa dinyalakan sampai terunduh."
  fi
  return 0
}
