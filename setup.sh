#!/bin/sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"

if [ ! -d "$SRC_DIR" ]; then
  printf '%s: direktori src/ tidak ditemukan: %s\n' "$0" "$SRC_DIR" >&2
  exit 1
fi

for _module in common config preflight gpu deps llama models env uv service helpers pi hexstrike finalize; do
  _file="$SRC_DIR/${_module}.sh"
  if [ ! -f "$_file" ]; then
    printf '%s: modul wajib hilang: %s\n' "$0" "$_file" >&2
    exit 1
  fi
  . "$_file"
done

main() {
  # Mode hanya-cek: tidak menyentuh sistem, tidak butuh root
  if [ "${1:-}" = "gpu-check" ] || [ "${GPU_CHECK_ONLY:-0}" = 1 ]; then
    detect_gpus
    report_gpus
    exit 0
  fi

  require_root_and_xbps
  validate_config

  # sudo -> SUDO_USER ; doas -> DOAS_USER
  REAL_USER="${SUDO_USER:-${DOAS_USER:-${USER:-}}}"
  REAL_HOME=""
  if [ -n "$REAL_USER" ]; then
    REAL_HOME=$(getent passwd "$REAL_USER" 2>/dev/null | cut -d: -f6)
  fi
  if [ -z "$REAL_HOME" ]; then
    warn "Home user biasa tidak ketemu (REAL_USER='${REAL_USER:-}'); langkah per-user (Pi, HexStrike, env shell) dilewati."
  elif [ "$REAL_USER" = root ]; then
    warn "Dijalankan sebagai root langsung. Langkah per-user (Pi, HexStrike, env shell) dilewati; jalankan lewat 'sudo' dari akun biasa."
  fi

  # catat lokasi sejak awal supaya uninstall.sh tahu bahkan bila setup terhenti di tengah
  write_state

  install_deps
  detect_gpus
  report_gpus

  install_official_llama
  download_models
  setup_env
  setup_service
  install_helpers

  install_pi
  install_uv
  install_hexstrike

  finalize
}

main "$@"
