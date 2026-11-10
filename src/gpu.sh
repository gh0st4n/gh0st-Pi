detect_gpus() {
  TOTAL=0
  N_INTEL=0
  N_AMD=0
  N_NVIDIA=0
  N_OTHER=0

  SUB_INTEL=""
  SUB_AMD=""
  SUB_NVIDIA=""
  SUB_OTHER=""

  DETAIL=""
  NEED_NVIDIA=0

  # (tidak memasang apa pun di sini: mode gpu-check harus aman tanpa root)
  for d in "${PCI_SYSFS:-/sys/bus/pci/devices}"/*; do
    if [ ! -d "$d" ]; then
      continue
    fi

    cls=$(cat "$d/class" 2>/dev/null) || continue
    if [ -z "$cls" ]; then
      continue
    fi

    base=${cls#0x}
    bc=$(printf '%s' "$base" | cut -c1-2)

    # 0x03 = display controller
    if [ "$bc" != "03" ]; then
      continue
    fi

    # subclass: 00=VGA/iGPU, 02=3D/dGPU
    sc=$(printf '%s' "$base" | cut -c3-4)

    vnd=$(cat "$d/vendor" 2>/dev/null)
    did=$(cat "$d/device" 2>/dev/null)
    bdf=$(basename "$d")

    case "$vnd" in
      0x8086) tag=intel ;;
      0x1002) tag=amd ;;
      0x10de) tag=nvidia ;;
      *) tag=other ;;
    esac

    TOTAL=$((TOTAL + 1))

    case "$tag" in
      intel)
        N_INTEL=$((N_INTEL + 1))
        SUB_INTEL="$SUB_INTEL $sc"
        ;;
      amd)
        N_AMD=$((N_AMD + 1))
        SUB_AMD="$SUB_AMD $sc"
        ;;
      nvidia)
        N_NVIDIA=$((N_NVIDIA + 1))
        SUB_NVIDIA="$SUB_NVIDIA $sc"
        NEED_NVIDIA=1
        ;;
      other)
        N_OTHER=$((N_OTHER + 1))
        SUB_OTHER="$SUB_OTHER $sc"
        ;;
    esac

    model="(sysfs $vnd:$did)"
    driver=""

    if have lspci; then
      m=$(lspci -s "$bdf" 2>/dev/null | cut -d: -f2- | sed 's/^ //')
      if [ -n "$m" ]; then
        model="$m"
      fi
      driver=$(lspci -k -s "$bdf" 2>/dev/null | sed -n 's/.*Kernel driver in use: //p')
    fi

    # newline di akhir WAJIB dipertahankan (jangan pakai $(printf ...) yang membuangnya)
    DETAIL="${DETAIL}${bdf}|${tag}|${sc}|${model}|${driver}
"
  done
}

classify_combo() {
  COMBO_LABEL=""
  COMBO_NOTE=""

  VSET=""
  if [ "$N_INTEL" -gt 0 ]; then VSET="$VSET intel"; fi
  if [ "$N_AMD" -gt 0 ]; then VSET="$VSET amd"; fi
  if [ "$N_NVIDIA" -gt 0 ]; then VSET="$VSET nvidia"; fi
  if [ "$N_OTHER" -gt 0 ]; then VSET="$VSET other"; fi

  # urutan sudah tetap (intel amd nvidia other); JANGAN di-sort (merusak pola case di bawah)
  # shellcheck disable=SC2086  # pemisahan kata disengaja
  set -- $VSET
  VSET="$*"

  dgpu=""
  igpu=""

  # BUG lama: eval "\$SUB_$t" dgn t huruf kecil -> variabel SUB_amd (kosong), bukan SUB_AMD.
  # Akibatnya iGPU/dGPU tidak pernah terdeteksi. Pakai nama variabel HURUF BESAR.
  for t in intel amd nvidia; do
    T=$(printf '%s' "$t" | tr '[:lower:]' '[:upper:]')
    eval "s=\$SUB_$T"
    case " $s " in
      *" 02 "*) dgpu="$t" ;;
    esac
  done

  for t in intel amd nvidia; do
    T=$(printf '%s' "$t" | tr '[:lower:]' '[:upper:]')
    eval "s=\$SUB_$T"
    if [ "$t" != "$dgpu" ]; then
      case " $s " in
        *" 00 "*)
          if [ -z "$igpu" ]; then
            igpu="$t"
          fi
          ;;
      esac
    fi
  done

  case "$VSET" in
    "intel")
      if [ "$TOTAL" -eq 1 ]; then
        COMBO_LABEL="intel only"
      else
        case " $SUB_INTEL " in
          *" 02 "*) COMBO_LABEL="intel + intel (iGPU + dGPU Arc)" ;;
          *) COMBO_LABEL="intel x$TOTAL (multi; cek class)" ;;
        esac
      fi
      ;;
    "amd")
      if [ "$TOTAL" -eq 1 ]; then
        COMBO_LABEL="amd only"
      else
        case " $SUB_AMD " in
          *" 02 "*) COMBO_LABEL="amd + amd (APU + dGPU)" ;;
          *) COMBO_LABEL="amd x$TOTAL (multi; cek class)" ;;
        esac
      fi
      ;;
    "nvidia")
      COMBO_LABEL="nvidia only (dGPU / workstation)"
      ;;
    "intel nvidia")
      COMBO_LABEL="intel + nvidia (iGPU Intel + dGPU Nvidia)"
      ;;
    "amd nvidia")
      COMBO_LABEL="amd + nvidia (iGPU AMD + dGPU Nvidia)"
      ;;
    "intel amd")
      if [ -n "$dgpu" ] && [ -n "$igpu" ] && [ "$igpu" != "$dgpu" ]; then
        if [ "$dgpu" = nvidia ]; then
          COMBO_LABEL="$igpu + nvidia"
        else
          COMBO_LABEL="$igpu + $dgpu(GPU)"
        fi
      else
        COMBO_LABEL="intel + amd (hybrid; arah iGPU/dGPU TIDAK pasti dari class)"
        COMBO_NOTE="Cek kolom DRIVER/CLASS: iGPU biasanya 0x0300+driver i915/amdgpu, dGPU 0x0302."
      fi
      ;;
    "intel amd nvidia")
      COMBO_LABEL="intel + amd + nvidia (triple, jarang)"
      ;;
    "")
      COMBO_LABEL="TIDAK ADA GPU display terdeteksi (headless/VM?)"
      ;;
    *)
      COMBO_LABEL="kombinasi lain: [$VSET]"
      ;;
  esac
}

select_vulkan_pkgs() {
  VULKAN_PKGS="Vulkan-Headers vulkan-loader"
  VULKAN_NOTE=""

  if [ "$N_INTEL" -gt 0 ]; then
    VULKAN_PKGS="$VULKAN_PKGS mesa-vulkan-intel"
  fi

  if [ "$N_AMD" -gt 0 ]; then
    VULKAN_PKGS="$VULKAN_PKGS mesa-vulkan-radeon"
  fi

  if [ "$NEED_NVIDIA" = 1 ]; then
    VULKAN_NOTE="Nvidia: utk llama.cpp pakai GH0ST_BACKEND=cuda (installer resmi unduh binari CUDA sendiri). Driver kernel nvidia TETAP perlu manual via repo void-repo-nonfree; TIDAK di-auto-install krn DKMS/secure-boot."
  fi

  if [ "$N_INTEL" -eq 0 ] && [ "$N_AMD" -eq 0 ] && [ "$NEED_NVIDIA" -eq 0 ]; then
    VULKAN_PKGS="$VULKAN_PKGS mesa-vulkan-lavapipe"
    VULKAN_NOTE="${VULKAN_NOTE:+$VULKAN_NOTE | }Tak ada GPU vendor -> lavapipe (CPU rasterizer; TIDAK utk offload)."
  fi
}

report_gpus() {
  classify_combo
  select_vulkan_pkgs

  if [ "$N_NVIDIA" -gt 0 ]; then
    REC="cuda  (butuh driver nvidia via void-repo-nonfree + reboot)"
  elif [ "$N_AMD" -gt 0 ]; then
    REC="rocm ATAU vulkan (mesa-vulkan-radeon); default cpu aman utk 16GB"
  elif [ "$N_INTEL" -gt 0 ]; then
    REC="vulkan (mesa-vulkan-intel) ATAU cpu (default, 16GB-safe)"
  else
    REC="cpu"
  fi

  printf '=================  LAPORAN GPU  =================\n'
  printf '%-14s %-7s %-6s %-44s %s\n' "BDF" "VENDOR" "CLASS" "MODEL" "DRIVER-IN-USE"

  printf '%s' "$DETAIL" | while IFS='|' read -r bdf tag sc model driver; do
    if [ -z "$bdf" ]; then
      continue
    fi
    printf '%-14s %-7s 0x03%s %-44s %s\n' "$bdf" "$tag" "$sc" "$model" "${driver:--}"
  done

  printf -- '------------------------------------------------\n'
  printf 'TOTAL device display : %s   (intel=%s amd=%s nvidia=%s other=%s)\n' "$TOTAL" "$N_INTEL" "$N_AMD" "$N_NVIDIA" "$N_OTHER"
  printf 'KOMBINASI            : %s\n' "$COMBO_LABEL"

  if [ -n "$COMBO_NOTE" ]; then
    printf 'CATATAN KLASIFIKASI : %s\n' "$COMBO_NOTE"
  fi

  printf 'REKOMENDASI BACKEND  : %s\n' "$REC"
  printf 'BACKEND AKTIF SKRIP  : %s   (ubah: sudo env GH0ST_BACKEND=... sh setup.sh)\n' "$GH0ST_BACKEND"
  printf 'PAKET VULKAN (ref.)  : %s   [TIDAK di-install jalur resmi; installer probe sendiri]\n' "$VULKAN_PKGS"

  if [ -n "$VULKAN_NOTE" ]; then
    printf 'CATATAN VULKAN      : %s\n' "$VULKAN_NOTE"
  fi

  printf '================================================\n'
}