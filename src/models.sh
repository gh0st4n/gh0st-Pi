download_models() {
  mkdir -p "$LLAMA_MODELS"
  need curl
  FAILED=""

  info "Unduh GGUF -> $LLAMA_MODELS (SSD; pindah ke HDD via env bila sesak, lihat [H])"

  while IFS='|' read -r repo file; do
    if [ -z "$repo" ]; then
      continue
    fi

    dest="$LLAMA_MODELS/$file"

    if [ -s "$dest" ]; then
      info "ada, skip: $file"
      continue
    fi

    url="https://huggingface.co/$repo/resolve/main/$file"
    tries=0
    ok=0

    while [ "$tries" -lt 3 ]; do
      if curl -fL --retry 2 --connect-timeout 20 -o "$dest.part" "$url"; then
        mv -f "$dest.part" "$dest"
        ok=1
        break
      fi

      tries=$((tries + 1))
      warn "gagal ($tries/3) $file; retry 10s"
      rm -f "$dest.part"
      sleep 10
    done

    if [ "$ok" != 1 ]; then
      warn "MENYERAH $file"
      FAILED="$FAILED $file"
    fi
  done <<EOF
$MODELS_LIST
EOF

  DEFAULT_MODEL="$LLAMA_MODELS/$DEFAULT_MODEL_FILE"

  if [ ! -s "$DEFAULT_MODEL" ]; then
    warn "Model default '$DEFAULT_MODEL_FILE' belum ada -> service llama gagal start smpai diunduh manual."
  fi
}