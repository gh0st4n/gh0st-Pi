install_deps() {
  info "Install dependensi inti via xbps (jalur DEFAULT llama = installer resmi, TANPA build C++)"

  # git utk HexStrike; curl+ca-certs utk unduh installer & GGUF; nodejs utk
  # REA/Pi-ext; python3 base venv HexStrike; procps-ng utk REA.
  if ! xbps-install -S git pkg-config curl ca-certificates nodejs python3 procps-ng 2>/dev/null; then
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

  # zstd OPSIONAL: kalau tak ada, installer resmi self-heal unduh helper unzstd.
  xbps_try zstd

  if have zstd; then
    info "zstd ada (installer pakai, tanpa unduh helper)"
  else
    info "zstd tak ada; installer resmi akan unduh helper unzstd sendiri (tetap jalan)"
  fi

  # cek versi Node utk REA (22>=22.19 / 24>=24.11 / 26+)
  nv=$(node -v 2>/dev/null | sed 's/^v//')
  info "node: ${nv:-?}"

  if [ -z "$nv" ]; then
    warn "node tak terdeteksi; REA/Pi-ext manual."
  elif node_ok "$nv"; then
    info "node $nv memenuhi syarat REA."
  else
    warn "Node $nv TIDAK memenuhi syarat REA (22.x>=22.19 / 24.x>=24.11 / 26+). Upgrade sebelum 'rea setup'."
  fi
}