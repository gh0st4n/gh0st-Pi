install_official_llama() {
  LLAMA_BIN="$LLAMA_HOME/.llama-app/llama"

  if [ -x "$LLAMA_BIN" ] && [ "$FORCE_BUILD" != "1" ]; then
    info "binari llama resmi sudah ada (skip). FORCE_BUILD=1 utk install ulang."
    if [ ! -e /usr/local/bin/llama ]; then
      ln -sf "$LLAMA_BIN" /usr/local/bin/llama 2>/dev/null || true
    fi
    return 0
  fi

  need curl

  case "$GH0ST_BACKEND" in
    cpu)
      BK="SKIP_CUDA=1 SKIP_ROCM=1 SKIP_VULKAN=1"
      ;;
    cuda)
      BK="SKIP_ROCM=1 SKIP_VULKAN=1"
      ;;
    rocm)
      BK="SKIP_CUDA=1 SKIP_VULKAN=1"
      ;;
    vulkan)
      BK="SKIP_CUDA=1 SKIP_ROCM=1"
      ;;
    auto)
      BK=""
      ;;
    *)
      warn "GH0ST_BACKEND='$GH0ST_BACKEND' tak dikenal; fallback cpu"
      BK="SKIP_CUDA=1 SKIP_ROCM=1 SKIP_VULKAN=1"
      ;;
  esac

  mkdir -p "$LLAMA_HOME"

  SI=""
  if [ "$GH0ST_SKIP_INSTALL" = "1" ]; then
    SI="SKIP_INSTALL=1"
  fi

  info "Installer resmi: HOME=$LLAMA_HOME (SSD) backend=$GH0ST_BACKEND skip_install=$GH0ST_SKIP_INSTALL"

  (
    export HOME="$LLAMA_HOME" $BK $SI

    if [ -n "$HF_TOKEN" ]; then
      export HF_TOKEN
      info "HF_TOKEN di-set (auth bucket / anti rate-limit)"
    fi

    if [ -n "$LLAMA_VERSION" ]; then
      export LLAMA_VERSION
      info "pin LLAMA_VERSION=$LLAMA_VERSION"
    fi

    if [ -n "$LLAMA_BUCKET" ]; then
      export LLAMA_BUCKET
      info "override LLAMA_BUCKET=$LLAMA_BUCKET"
    fi

    if have curl; then
      curl -LsSf https://llama.app/install.sh | sh
    else
      wget -qO- https://llama.app/install.sh | sh
    fi
  ) || err "installer resmi GAGAL (die 111). Cek output/koneksi/HF bucket; pin LLAMA_VERSION bila perlu."

  if [ ! -x "$LLAMA_BIN" ]; then
    err "$LLAMA_BIN tak ada pasca-install (HOME override gagal?)"
  fi

  ver=$("$LLAMA_BIN" version 2>/dev/null) || err "binari tak bisa dieksekusi (linking?): $LLAMA_BIN"
  info "llama version: $ver"

  if [ -n "$SI" ] && [ -n "$LLAMA_VERSION" ]; then
    warn "SKIP_INSTALL + LLAMA_VERSION di-set: upstream TIDAK verifikasi pin. Yakin '$ver' = $LLAMA_VERSION?"
  fi

  ln -sf "$LLAMA_BIN" /usr/local/bin/llama 2>/dev/null || warn "gagal symlink /usr/local/bin/llama"
  info "symlink global: /usr/local/bin/llama -> $LLAMA_BIN"

  if ! "$LLAMA_BIN" serve --help 2>&1 | grep -q -- '--model'; then
    warn "'llama serve --help' tak menyebut '--model'; flag server mungkin beda versi."
    warn "WAJIB verifikasi API utk pilar [1] setelah service naik (lihat setup_service & [G])."
  fi
}