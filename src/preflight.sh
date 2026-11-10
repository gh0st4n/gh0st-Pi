require_root_and_xbps() {
  if [ "$(id -u)" -ne 0 ]; then
    err "Butuh root. Jalankan: sudo sh setup.sh"
  fi

  # ---------------------------------------------------------------------
  # Gerbang utama: package manager yang benar-benar dipakai script.
  # ---------------------------------------------------------------------
  if ! have xbps-install; then
    if [ -x /usr/bin/xbps-install ]; then
      PATH="/usr/bin:${PATH}"
    elif [ -x /bin/xbps-install ]; then
      PATH="/bin:${PATH}"
    else
      err "XBPS tidak ditemukan. Installer ini untuk Void/T4n OS."
    fi
  fi

  if ! xbps-install --version >/dev/null 2>&1; then
    err "xbps-install ditemukan tetapi tidak dapat dijalankan."
  fi

  # ---------------------------------------------------------------------
  # Service dibuat di /etc/sv (runit) dan dijalankan lewat 'chpst'
  # ---------------------------------------------------------------------
  if ! have sv && [ ! -d "$RN" ]; then
    err "runit/sv tidak ditemukan. Installer ini membuat service runit."
  fi
  if ! have chpst; then
    err "'chpst' (paket runit) tidak ditemukan; dibutuhkan agar service jalan tanpa root."
  fi
  if ! have useradd; then
    err "'useradd' tidak ditemukan (paket shadow); dibutuhkan utk user service '$LLAMA_USER'."
  fi
  if ! have sha256sum; then
    err "'sha256sum' (coreutils) tidak ditemukan."
  fi

  # ---------------------------------------------------------------------
  # /etc/os-release hanya utk identitas dan warning, bukan gate utama.
  # Void asli: ID=void (tanpa ID_LIKE). T4n: ID=t4n atau ID_LIKE berisi void.
  # ---------------------------------------------------------------------
  OS_ID=""
  OS_LIKE=""

  if [ -r /etc/os-release ]; then
    OS_ID=$(sed -n 's/^ID=//p' /etc/os-release | head -n1 | tr -d '"' | tr -d '\r')
    OS_LIKE=$(sed -n 's/^ID_LIKE=//p' /etc/os-release | head -n1 | tr -d '"' | tr -d '\r')
  fi

  known_distro=0
  case " ${OS_ID} ${OS_LIKE} " in
    *" t4n "*|*" void "*)
      known_distro=1
      ;;
  esac

  if [ "$known_distro" -ne 1 ]; then
    warn "OS release tidak dikenali sebagai T4n/Void (ID='${OS_ID}', ID_LIKE='${OS_LIKE}'), tetapi xbps dan runit tersedia. Melanjutkan."
  fi
}

# Semua path yang akan ditulis ke file konfigurasi harus absolut & tanpa spasi/kutip.
validate_config() {
  for _v in GH0ST_ROOT LLAMA_HOME LLAMA_MODELS UV_HOME HEX_DIR HEX_ENV HEX_CACHE WORKSPACE SV RN SVLOG_DIR BIN_DIR LLAMA_STATE; do
    eval "_val=\$$_v"
    if ! safe_abs_path "$_val"; then
      err "$_v='$_val' tidak valid (harus path absolut tanpa spasi/kutip)."
    fi
  done

  # LLAMA_HOME/UV_HOME di-chown ke root secara rekursif; jangan sampai itu folder home user.
  for _v in LLAMA_HOME UV_HOME; do
    eval "_val=\$$_v"
    case "$_val" in
      /home|/home/)
        err "$_v tidak boleh '$_val'"
        ;;
      /home/*)
        _rest=${_val#/home/}
        case "$_rest" in
          */*) : ;;
          *) err "$_v tidak boleh langsung folder home user ($_val)" ;;
        esac
        ;;
    esac
  done

  case "$GH0ST_ROOT" in
    /|/opt|/home|/usr|/var|/etc|/root)
      err "GH0ST_ROOT terlalu berbahaya: $GH0ST_ROOT"
      ;;
  esac

  case "$PORT$CTX$HEX_PORT" in
    *[!0-9]*) err "GH0ST_PORT / GH0ST_CTX / HEX_PORT harus angka." ;;
  esac

  case "$GH0ST_THINKING" in
    on|off) : ;;
    *) err "GH0ST_THINKING harus 'on' atau 'off'." ;;
  esac

  case "$DEFAULT_MODEL_FILE" in
    */*|*"'"*|*" "*|"") err "GH0ST_DEFAULT_MODEL tidak valid: '$DEFAULT_MODEL_FILE'" ;;
  esac
}
