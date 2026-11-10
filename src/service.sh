# conf_get FILE KEY -> nilai (tanpa kutip) atau kosong
conf_get() {
  sed -n "s/^$2='\(.*\)'\$/\1/p" "$1" 2>/dev/null | head -n 1
}

setup_service() {
  info "Siapkan runit service di $SV (jalan sbg user '$LLAMA_USER', BUKAN root)"
  ensure_llama_user
  mkdir -p "$SV/log" "$SVLOG_DIR"
  chmod 750 "$SVLOG_DIR"

  # Pilihan model/thinking dari konfigurasi lama dipertahankan saat setup diulang,
  # kecuali kamu memberi nilai baru lewat environment.
  ACTIVE_MODEL="$DEFAULT_MODEL_FILE"
  THINK="$GH0ST_THINKING"
  if [ -f "$SV/conf" ]; then
    if [ -z "${GH0ST_DEFAULT_MODEL:-}" ]; then
      _old=$(conf_get "$SV/conf" MODEL_FILE)
      if [ -n "$_old" ] && [ -s "$LLAMA_MODELS/$_old" ]; then
        ACTIVE_MODEL="$_old"
      fi
    fi
    if [ -z "$THINK_EXPLICIT" ]; then
      _oldt=$(conf_get "$SV/conf" THINK)
      if [ -n "$_oldt" ]; then
        THINK="$_oldt"
      fi
    fi
  fi

  if [ -z "$LLAMA_HELP" ] && [ -x "$LLAMA_BIN" ]; then
    llama_probe_flags
  fi
  build_llama_flags

  cat > "$SV/conf" <<EOF
# gh0st-pi: konfigurasi service llama. Ubah lewat 'gh0st-ai' (atau edit manual, lalu 'gh0st-ai restart').
MODEL_FILE='$ACTIVE_MODEL'
MODELS_DIR='$LLAMA_MODELS'
LLAMA_BIN='$LLAMA_BIN'
RUN_USER='$LLAMA_USER'
STATE_DIR='$LLAMA_STATE'
SERVE_SUBCMD='serve'
PORT='$PORT'
CTX='$CTX'
EXTRA_FLAGS='$EXTRA_FLAGS'
HAS_REASONING='${HAS_REASONING:-0}'
THINK='$THINK'
EOF
  chmod 644 "$SV/conf"

  cat > "$SV/run" <<'EOF'
#!/bin/sh
# gh0st-pi: server llama. Berjalan sbg user biasa (RUN_USER), BUKAN root.
# Bind localhost saja. Pengaturan ada di ./conf (ubah lewat 'gh0st-ai').
exec 2>&1
. ./conf

MODEL="$MODELS_DIR/$MODEL_FILE"
if [ ! -s "$MODEL" ]; then
  echo "gh0st-pi: model tidak ditemukan: $MODEL"
  echo "gh0st-pi: pilih model lain dengan 'gh0st-ai model' (service dimatikan agar tidak looping)"
  sv down .
  exit 1
fi

cd "$STATE_DIR" || exit 1

# SERVE_SUBCMD=serve utk binari 'llama' (installer resmi); kosongkan utk 'llama-server' hasil build sendiri.
SERVE_SUBCMD="${SERVE_SUBCMD-serve}"
# shellcheck disable=SC2086
set -- $SERVE_SUBCMD --model "$MODEL" --host 127.0.0.1 --port "$PORT" --ctx-size "$CTX" --parallel 1
if [ "$HAS_REASONING" = 1 ] && [ "$THINK" = off ]; then
  set -- "$@" --reasoning off
fi

# shellcheck disable=SC2086
exec chpst -u "$RUN_USER" env HOME="$STATE_DIR" "$LLAMA_BIN" "$@" $EXTRA_FLAGS
EOF
  chmod 755 "$SV/run"

  printf '#!/bin/sh\nexec svlogd -tt %s\n' "$SVLOG_DIR" > "$SV/log/run"
  chmod 755 "$SV/log/run"

  if [ "$GH0ST_AUTOSTART" = 1 ]; then
    rm -f "$SV/down"
    info "AI akan nyala otomatis saat boot (GH0ST_AUTOSTART=1)."
  else
    touch "$SV/down"
    info "AI TIDAK nyala otomatis saat boot (hemat RAM). Nyalakan: gh0st-ai start"
  fi

  if [ ! -d "$RN" ]; then
    warn "$RN tidak ada; service tidak ditautkan ke runit."
    LLAMA_SMOKE="dilewati (runsvdir tidak ditemukan)"
    return 0
  fi

  if [ -L "$RN/llama" ] || [ -e "$RN/llama" ]; then
    info "service sudah link, skip"
  else
    ln -s "$SV" "$RN/llama"
    info "link $SV -> $RN/llama"
  fi

  info "tunggu runsvdir mengambil service..."
  tries=0
  while [ ! -e "$RN/llama/supervise/ok" ]; do
    tries=$((tries + 1))
    if [ "$tries" -ge 15 ]; then
      warn "runsvdir lambat; lanjut"
      break
    fi
    sleep 1
  done

  # ---- Tes sekali jalan: nyalakan, pastikan API menjawab, lalu matikan lagi ----
  _model="$LLAMA_MODELS/$ACTIVE_MODEL"
  if [ ! -s "$_model" ]; then
    LLAMA_SMOKE="dilewati (model '$ACTIVE_MODEL' belum ada)"
    warn "$LLAMA_SMOKE"
    return 0
  fi

  if ! chpst -u "$LLAMA_USER" test -r "$_model"; then
    warn "user '$LLAMA_USER' TIDAK bisa membaca $_model."
    warn "Biasanya karena model ada di dalam /home yang tertutup. Beri izin lewat: chmod o+x <folder induk>, atau taruh model di /opt."
  fi

  info "tes nyalakan AI (memuat model dari disk, 10-90 detik)..."
  sv down "$SV" >/dev/null 2>&1 || true
  sleep 1
  sv up "$SV" >/dev/null 2>&1 || true

  tries=0
  LLAMA_SMOKE="GAGAL"
  while [ "$tries" -lt "$READY_TIMEOUT" ]; do
    # gerbang SEBENARNYA: /v1/models mengembalikan daftar model (itu yg dipakai Pi),
    # bukan /health (bisa 200 padahal Pi tidak melihat model).
    if curl -fsS --max-time 3 "http://127.0.0.1:$PORT/v1/models" 2>/dev/null | grep -q '"data"'; then
      LLAMA_SMOKE="OK"
      break
    fi
    tries=$((tries + 1))
    sleep 1
  done

  if [ "$LLAMA_SMOKE" = "OK" ]; then
    info "/v1/models OK (model terlihat oleh Pi)"
  else
    if curl -s -o /dev/null -w '%{http_code}' --max-time 3 "http://127.0.0.1:$PORT/health" 2>/dev/null | grep -q '^200$'; then
      LLAMA_SMOKE="GAGAL (/health 200 tapi /v1/models tanpa daftar model)"
      warn "$LLAMA_SMOKE"
      warn "'llama serve' mungkin tidak kompatibel dgn pi-llama-cpp. Lihat README: 'Fallback build llama-server'."
    else
      LLAMA_SMOKE="GAGAL (tidak siap dalam ${READY_TIMEOUT}s)"
      warn "$LLAMA_SMOKE. Cek: gh0st-ai status  dan  gh0st-ai log"
    fi
    if [ -f "$SVLOG_DIR/current" ]; then
      warn "--- 15 baris terakhir log ---"
      tail -n 15 "$SVLOG_DIR/current" >&2
    fi
  fi

  if [ "$GH0ST_AUTOSTART" != 1 ]; then
    sv down "$SV" >/dev/null 2>&1 || true
    info "AI dimatikan lagi (RAM dibebaskan). Nyalakan kapan perlu: gh0st-ai start"
  fi

  info "llama service: http://127.0.0.1:$PORT  (status: gh0st-ai status)"
  return 0
}
