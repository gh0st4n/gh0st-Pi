# State file: sentinel + catatan lokasi, dibaca uninstall.sh (milik root).
write_state() {
  install -d -m 755 -o root -g root "$GH0ST_ROOT"
  _files=$(printf '%s\n' "$MODELS_LIST" | cut -d'|' -f2 | tr '\n' ' ')
  # gabungkan dgn catatan lama: setup yg diulang dgn MODELS_LIST berbeda jangan "melupakan" model sebelumnya
  if [ -f "$STATE_FILE" ]; then
    _prev=$(sed -n "s/^MODEL_FILES='\(.*\)'\$/\1/p" "$STATE_FILE" | head -n 1)
    _files=$(printf '%s %s\n' "$_prev" "$_files" | tr ' ' '\n' | grep -v '^$' | sort -u | tr '\n' ' ')
  fi
  {
    printf '# gh0st-pi state: dibuat oleh setup.sh, dibaca uninstall.sh. Jangan diubah.\n'
    printf "GH0ST_ROOT='%s'\n" "$GH0ST_ROOT"
    printf "LLAMA_HOME='%s'\n" "$LLAMA_HOME"
    printf "LLAMA_MODELS='%s'\n" "$LLAMA_MODELS"
    printf "UV_HOME='%s'\n" "$UV_HOME"
    printf "HEX_DIR='%s'\n" "$HEX_DIR"
    printf "HEX_CACHE='%s'\n" "$HEX_CACHE"
    printf "WORKSPACE='%s'\n" "$WORKSPACE"
    printf "SV='%s'\n" "$SV"
    printf "RN='%s'\n" "$RN"
    printf "SVLOG_DIR='%s'\n" "$SVLOG_DIR"
    printf "BIN_DIR='%s'\n" "$BIN_DIR"
    printf "LLAMA_USER='%s'\n" "$LLAMA_USER"
    printf "LLAMA_STATE='%s'\n" "$LLAMA_STATE"
    printf "MODEL_FILES='%s'\n" "${_files% }"
  } > "$STATE_FILE"
  chown root:root "$STATE_FILE"
  chmod 644 "$STATE_FILE"
}

# Yang dieksekusi service/root TIDAK boleh bisa ditulis user biasa.
# (Versi lama men-chown -R seluruh $GH0ST_ROOT ke user, sehingga binari yg dijalankan root
#  bisa ditimpa user -> eskalasi ke root. Di sini dikembalikan ke root.)
harden_perms() {
  chown root:root "$GH0ST_ROOT" 2>/dev/null || true
  if [ -d "$GH0ST_ROOT/tools" ]; then
    chown root:root "$GH0ST_ROOT/tools" 2>/dev/null || true
  fi
  if [ -f "$GH0ST_ROOT/tools/hexstrike_local.py" ]; then
    chown root:root "$GH0ST_ROOT/tools/hexstrike_local.py" 2>/dev/null || true
  fi

  for d in "$LLAMA_HOME" "$UV_HOME"; do
    if [ -d "$d" ]; then
      chown -R root:root "$d" 2>/dev/null || true
    fi
  done

  # yang MEMANG milik user: workspace kerja, source+venv+cache HexStrike
  if [ -n "$REAL_USER" ] && [ "$REAL_USER" != root ]; then
    _grp=$(id -gn "$REAL_USER" 2>/dev/null || echo "$REAL_USER")
    install -d -o "$REAL_USER" -g "$_grp" -m 755 "$WORKSPACE"
    for d in "$HEX_DIR" "$HEX_CACHE"; do
      if [ -d "$d" ]; then
        chown -R "$REAL_USER:$_grp" "$d" 2>/dev/null || true
      fi
    done
  fi
}

finalize() {
  harden_perms
  write_state

  shell=""
  if [ -n "$REAL_HOME" ]; then
    if [ -f "$REAL_HOME/.bashrc" ]; then shell="$REAL_HOME/.bashrc"; fi
    if [ -f "$REAL_HOME/.zshrc" ]; then shell="$REAL_HOME/.zshrc"; fi
    if [ -f "$REAL_HOME/.config/fish/config.fish" ]; then shell="$REAL_HOME/.config/fish/config.fish"; fi
  fi

  if [ "$HEX_OK" = 1 ]; then
    hex_txt="siap (jalankan: gh0st-hexstrike)"
  elif [ "$GH0ST_INSTALL_HEXSTRIKE" != 1 ]; then
    hex_txt="dilewati"
  else
    hex_txt="BELUM siap (lihat peringatan di atas)"
  fi

  info "================ gh0st-pi selesai ================"
  info "AI lokal (llama) : $LLAMA_SMOKE"
  info "Versi llama      : ${LLAMA_VER:-?}"
  info "Model default    : ${ACTIVE_MODEL:-$DEFAULT_MODEL_FILE}"
  info "Pi (agent coding): $PI_STATUS"
  info "HexStrike        : $hex_txt"
  info "Folder           : $GH0ST_ROOT   (model: $LLAMA_MODELS)"
  info "Log AI           : $SVLOG_DIR/current"

  if [ -n "$FAILED" ]; then
    warn "Model GAGAL diunduh:$FAILED  -> jalankan ulang 'sudo sh setup.sh' (unduhan yang terputus DILANJUTKAN; file yang gagal verifikasi diunduh ulang)"
  fi

  cat <<EOF

----------------------- CARA PAKAI (3 langkah) -----------------------
 1. Nyalakan AI      :  gh0st-ai start
 2. Ngobrol          :  buka browser -> http://127.0.0.1:$PORT   (seperti ChatGPT, tapi offline)
 3. Agent coding     :  buka TERMINAL BARU, ketik:  pi   lalu ketik:  /models
 Selesai? Matikan    :  gh0st-ai stop      (membebaskan RAM)

 Cek jawaban AI      :  gh0st-ai test      | ganti model:  gh0st-ai model
 Semua perintah      :  gh0st-ai help
 Panduan bahasa awam :  $SCRIPT_DIR/PANDUAN.md
 Detail teknis       :  $SCRIPT_DIR/README.md

 PENTING: HexStrike hanya lewat 'gh0st-hexstrike'. JANGAN jalankan
 hexstrike_server.py langsung (membuka server ke seluruh jaringan tanpa password).
----------------------------------------------------------------------
EOF

  if [ -n "$shell" ]; then
    info "Agar variabel env aktif: buka terminal baru, atau: source $shell"
  fi
  return 0
}
