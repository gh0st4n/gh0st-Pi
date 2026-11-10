# Newline literal (dipakai utk validasi nilai)
NL='
'

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

# Selalu return 0 (aman di bawah 'set -e'); gagal = warning saja.
xbps_try() {
  if ! xbps-install -Sy "$1"; then
    warn "xbps '$1' gagal (cek nama paket di voidlinux.org/packages)"
  fi
  return 0
}

# Path/nilai aman utk ditulis ke file konfigurasi shell (tanpa kutip/newline, absolut).
safe_abs_path() {
  case "$1" in
    /*) : ;;
    *) return 1 ;;
  esac
  case "$1" in
    *"'"*|*"$NL"*|*" "*) return 1 ;;
  esac
  return 0
}

sha256_of() {
  sha256sum "$1" | cut -d' ' -f1
}

# fetch_script URL DEST [SHA256_DIHARAPKAN]
# Unduh ke FILE (bukan 'curl | sh'), catat hash-nya, verifikasi bila diberi.
fetch_script() {
  if ! curl -fsSL --connect-timeout 20 -o "$2" "$1"; then
    warn "gagal unduh: $1"
    return 1
  fi

  _fs_hash=$(sha256_of "$2")
  _fs_size=$(wc -c < "$2" | tr -d ' ')
  info "unduh $1  (sha256=$_fs_hash, $_fs_size byte)"

  if [ -n "${3:-}" ] && [ "$3" != "$_fs_hash" ]; then
    warn "sha256 TIDAK cocok (diharapkan $3). Dibatalkan."
    rm -f "$2"
    return 1
  fi

  return 0
}

# run_as USER HOME perintah...  -> jalankan sebagai user biasa (BUKAN root)
run_as() {
  _ra_user=$1
  _ra_home=$2
  shift 2

  if [ "$(id -u)" -ne 0 ] || [ "$_ra_user" = root ]; then
    env HOME="$_ra_home" "$@"
  else
    chpst -u "$_ra_user" env HOME="$_ra_home" "$@"
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

# pi_node_ok MAJOR.MINOR -> 0 jika Node >= 22.19 (syarat paket Pi)
pi_node_ok() {
  _nv=$1
  case "$_nv" in
    *.*) : ;;
    *)   return 1 ;;
  esac

  _maj=${_nv%%.*}
  _rest=${_nv#*.}
  _min=${_rest%%.*}
  : "${_min:=0}"

  if [ "$_maj" -gt 22 ] 2>/dev/null; then
    return 0
  fi
  if [ "$_maj" = 22 ] && [ "$_min" -ge 19 ]; then
    return 0
  fi

  return 1
}
