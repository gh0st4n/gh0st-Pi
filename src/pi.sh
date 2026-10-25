install_pi_ext() {
  if ! have pi; then
    warn "'pi' tak di PATH root; ekstensi Pi dilewati. Manual sbg user: pi install npm:<ext>"
    return 0
  fi

  PI_FAIL=""

  for ext in $PI_EXT_LIST; do
    if pi install "npm:$ext" 2>/dev/null; then
      info "pi ext OK: $ext"
    else
      warn "pi install npm:$ext gagal (mungkin interaktif / jaringan); ulangi manual"
      PI_FAIL="$PI_FAIL $ext"
    fi
  done

  case " $PI_FAIL " in
    *" pi-llama-cpp "*)
      if pi install https://github.com/gsanhueza/pi-llama-cpp 2>/dev/null; then
        info "pi ext OK (github fallback): pi-llama-cpp"
        PI_FAIL=$(printf '%s' "$PI_FAIL" | sed 's/ pi-llama-cpp//')
      else
        warn "pi-llama-cpp gagal via npm & github"
      fi
      ;;
  esac

  if [ -n "$PI_FAIL" ]; then
    warn "Ekstensi Pi GAGAL (ulangi/manual):$PI_FAIL"
  fi
}