#!/bin/sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"

if [ ! -d "$SRC_DIR" ]; then
  printf '%s: direktori src/ tidak ditemukan: %s\n' "$0" "$SRC_DIR" >&2
  exit 1
fi

for _module in common config preflight gpu deps llama models env uv service pi hexstrike finalize; do
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

  require_root_and_distro

  REAL_USER="${SUDO_USER:-$USER}"
  REAL_HOME=$(getent passwd "$REAL_USER" 2>/dev/null | cut -d: -f6)
  if [ -z "$REAL_HOME" ]; then
    warn "Home '$REAL_USER' tak ketemu; langkah per-user mungkin dilewati."
  fi

  install_deps
  detect_gpus
  report_gpus

  install_official_llama
  download_models
  setup_env
  setup_service

  install_pi_ext
  install_uv
  install_hexstrike

  finalize
}

main "$@"