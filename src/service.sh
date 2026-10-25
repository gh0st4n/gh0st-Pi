setup_service() {
  info "Siapkan runit service di $SV"
  mkdir -p "$SV"

  cat > "$SV/run" <<EOF
#!/bin/sh
# gh0st-pi llama.cpp server via installer RESMI (binari 'llama serve', SSD).
# Bind localhost-only = aman dr LAN.
# Indikator 'Sleeping' di Pi HANYA muncul di mode router + --sleep-idle-seconds ([D]).
export HOME=$LLAMA_HOME
export LLAMA_MODELS=$LLAMA_MODELS
exec $LLAMA_BIN serve --model $LLAMA_MODELS/$DEFAULT_MODEL_FILE --host 127.0.0.1 --port $PORT --ctx-size $CTX --n-gpu-layers $NGPU --parallel 1 --cont-batching
EOF

  chmod +x "$SV/run"

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

  sv start llama >/dev/null 2>&1 || true

  info "tunggu llama-server ready (load model dr disk 10-90s)..."
  tries=0

  # gerbang SEBENARNYA utk pilar [1] = /v1/models mengembalikan daftar model,
  # bukan /health (yang bisa 200 padahal Pi buta model).
  until curl -fsS "http://127.0.0.1:$PORT/v1/models" 2>/dev/null | grep -q '"data"'; do
    tries=$((tries + 1))
    if [ "$tries" -ge 120 ]; then
      if curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/health" 2>/dev/null | grep -q '^200$'; then
        warn "/health 200 TAPI /v1/models tak mengembalikan daftar model ('data')."
        warn "Kemungkinan 'llama serve' BUKAN llama-server-compatible => pi-llama-cpp takkan lihat model."
        warn "Utk PILAR [1] pakai fallback build-from-source llama-server (NEXT STEPS [G]). Cek: sudo sv log llama"
      else
        err "llama-server tak ready 120s. 'sudo sv status llama' & 'sudo sv log llama'."
      fi
      break
    fi
    sleep 1
  done

  if [ "$tries" -lt 120 ]; then
    info "/v1/models OK (model terlihat oleh Pi)"
  fi

  info "llama service: http://127.0.0.1:$PORT  (status: sudo sv status llama)"
}