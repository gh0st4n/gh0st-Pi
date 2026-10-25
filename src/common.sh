err() {
  printf '%s: %s\n' "$0" "$*" >&2
  exit 1
}

warn() {
  printf '%s: WARN: %s\n' "$0" "$*" >&2
}

info() {
  printf '%s: %s\n' "$0" "$*" >&2
}

have() {
  command -v "$1" >/dev/null 2>&1
}

need() {
  if ! have "$1"; then
    err "Tool wajib hilang: $1"
  fi
}

xbps_try() {
  if ! xbps-install -S "$1" 2>/dev/null; then
    warn "xbps '$1' gagal (verifikasi nama di voidlinux.org/packages)"
  fi
}

# node_ok MAJOR.MINOR[.PATCH] -> 0 jika penuhi syarat REA (22>=22.19 / 24>=24.11 / 26+)
node_ok() {
  _nv=$1
  if [ -z "$_nv" ]; then
    return 1
  fi

  case "$_nv" in
    *.*) : ;;
    *)   return 1 ;;
  esac

  _maj=${_nv%%.*}
  _rest=${_nv#*.}
  _min=${_rest%%.*}
  : "${_min:=0}"

  if [ "$_maj" -ge 26 ] 2>/dev/null; then
    return 0
  fi
  if [ "$_maj" = 24 ] && [ "$_min" -ge 11 ]; then
    return 0
  fi
  if [ "$_maj" = 22 ] && [ "$_min" -ge 19 ]; then
    return 0
  fi

  return 1
}