require_root_and_xbps() {
  if [ "$(id -u)" -ne 0 ]; then
    err "Requires root, run with sudo"
  fi

  # ---------------------------------------------------------------------
  # Gerbang utama: package manager yang benar-benar dipakai script.
  # Tanpa xbps-install, installer tidak bisa bekerja dengan asumsi Void/T4n.
  # ---------------------------------------------------------------------
  if ! have xbps-install; then
    # Beberapa environment punya PATH sempit; cek lokasi umum.
    if [ -x /usr/bin/xbps-install ]; then
      PATH="/usr/bin:${PATH}"
    elif [ -x /bin/xbps-install ]; then
      PATH="/bin:${PATH}"
    else
      err "XBPS package manager not found. This installer targets Void/T4n OS."
    fi
  fi

  # Pastikan xbps-install benar-benar bisa dieksekusi, bukan sekadar ada di PATH.
  if ! xbps-install --version >/dev/null 2>&1; then
    err "xbps-install ditemukan tetapi tidak dapat dijalankan."
  fi

  # ---------------------------------------------------------------------
  # Gerbang tambahan: script ini membuat service runit di /etc/sv.
  # Kalau sistem tidak punya runit/sv, sebaiknya gagal lebih awal.
  # ---------------------------------------------------------------------
  if ! have sv && [ ! -d /etc/runit/runsvdir/default ]; then
    err "runit/sv not found. This installer creates services under /etc/sv."
  fi

  # ---------------------------------------------------------------------
  # /etc/os-release hanya untuk identitas dan warning, bukan gate utama.
  # ---------------------------------------------------------------------
  OS_ID=""
  OS_LIKE=""

  if [ -r /etc/os-release ]; then
    OS_ID=$(sed -n 's/^ID=//p' /etc/os-release | head -n1 | tr -d '"' | tr -d '\r')
    OS_LIKE=$(sed -n 's/^ID_LIKE=//p' /etc/os-release | head -n1 | tr -d '"' | tr -d '\r')
  fi

  known_distro=0

  case " ${OS_ID} ${OS_LIKE} " in
    *" t4n "*)
      known_distro=1
      ;;
  esac

  case " ${OS_LIKE} " in
    *" void "*)
      known_distro=1
      ;;
  esac

  if [ "$known_distro" -ne 1 ]; then
    warn "OS release tidak dikenali sebagai T4n/Void (ID='${OS_ID}', ID_LIKE='${OS_LIKE}'), tetapi xbps dan runit tersedia. Melanjutkan."
  fi
}