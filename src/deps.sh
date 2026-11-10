install_deps() {
  info "Install dependensi inti via xbps (llama dipasang dari installer resmi, TANPA build C++)"

  # git utk HexStrike; curl+ca-certs utk unduh installer & GGUF; nodejs utk Pi;
  # python3 base venv HexStrike; procps-ng utk REA; shadow/runit sudah wajib di preflight.
  if ! xbps-install -Sy git pkg-config curl ca-certificates nodejs python3 procps-ng; then
    err "xbps-install paket inti gagal. Cek koneksi/repo & nama paket di voidlinux.org/packages."
  fi

  if ! have git; then
    err "git hilang"
  fi
  if ! have curl; then
    err "curl hilang"
  fi
  if ! have node; then
    err "node hilang (paket nodejs)"
  fi
  if ! have python3; then
    err "python3 hilang (base venv HexStrike)"
  fi
  if ! have ps; then
    warn "'ps' tak di PATH walau procps-ng dicoba; REA ownership check bisa gagal."
  fi

  # zstd: installer llama butuh dekompresor. Tanpa zstd sistem, installer mengunduh helper
  # sendiri, dan ada laporan bug di mana itu menghasilkan binari 0 byte (kegagalan diam-diam).
  # Karena itu zstd DIANJURKAN; skrip ini juga memeriksa ukuran binari hasil pasang.
  xbps_try zstd
  if have zstd; then
    info "zstd ada"
  else
    warn "zstd TIDAK ada: installer llama bisa gagal diam-diam. Pasang manual: sudo xbps-install -S zstd"
  fi

  # pciutils hanya utk laporan GPU yang lebih jelas (opsional)
  if ! have lspci; then
    xbps_try pciutils
  fi

  if ! have npm; then
    warn "npm tidak ada (paket nodejs di Void biasanya menyertakannya); Pi tidak bisa dipasang otomatis."
  fi

  # cek versi Node: Pi butuh >=22.19; REA butuh 22>=22.19 / 24>=24.11 / 26+
  nv=$(node -v 2>/dev/null | sed 's/^v//')
  info "node: ${nv:-?}"

  if [ -z "$nv" ]; then
    warn "node tak terdeteksi; Pi/REA manual."
  elif pi_node_ok "$nv"; then
    info "node $nv memenuhi syarat Pi (>=22.19)."
    if ! node_ok "$nv"; then
      warn "Node $nv cukup utk Pi tapi di luar daftar versi REA (22.x>=22.19 / 24.x>=24.11 / 26+)."
    fi
  else
    warn "Node $nv TERLALU TUA utk Pi (butuh >=22.19). Upgrade nodejs dulu; Pi akan dilewati."
  fi
}
