# Pasang perintah bantu 'gh0st-ai' (template di bin/, path diisi saat pasang)
install_helpers() {
  _src="$SCRIPT_DIR/bin/gh0st-ai"
  if [ ! -f "$_src" ]; then
    warn "$_src tidak ada; perintah 'gh0st-ai' dilewati."
    return 0
  fi

  mkdir -p "$BIN_DIR"
  _tmp=$(mktemp)
  sed -e "s|@SV@|$SV|g" -e "s|@LOGDIR@|$SVLOG_DIR|g" "$_src" > "$_tmp"
  install -m 755 -o root -g root "$_tmp" "$BIN_DIR/gh0st-ai"
  rm -f "$_tmp"
  info "perintah bantu: $BIN_DIR/gh0st-ai  (start | stop | status | model | test | log)"
  return 0
}
