#!/bin/sh
# uninstall.sh - Uninstaller untuk gh0st-pi
#
# Prinsip:
#   - Melepas service runit llama dan user sistem '_llama'
#   - Membersihkan artefak yang DIPASANG setup.sh (lokasinya dibaca dari state file)
#   - Membersihkan env block di rc shell user (hanya baris milik gh0st-pi)
#   - TIDAK menghapus Pi, ~/.pi, tool eksternal, atau workspace kecuali diminta
#
# Usage:
#   sudo sh uninstall.sh [options]
#
# Options:
#   --keep-models         Jangan hapus file model GGUF
#   --purge-workspace     Hapus workspace
#   --purge-all           Hapus seluruh /opt/gh0st-pi dan /opt/llama
#   --dry-run             Tampilkan aksi, jangan ubah sistem
#   -y, --yes             Tanpa konfirmasi
#   --try-pi-uninstall    Coba lepas ekstensi Pi yang dipasang setup.sh
#   --keep-opt-llama      Jangan sentuh /opt/llama (varian lama build-dari-source)
#   --force               Izinkan hapus GH0ST_ROOT non-default tanpa state file
#   -h, --help            Tampilkan bantuan

set -e

err()  { printf '%s: %s\n' "$0" "$*" >&2; exit 1; }
info() { printf '%s: %s\n' "$0" "$*" >&2; }
warn() { printf '%s: WARN: %s\n' "$0" "$*" >&2; }
have() { command -v "$1" >/dev/null 2>&1; }

usage() {
    cat <<'EOF'
Usage: sudo sh uninstall.sh [options]

Options:
  --keep-models         Jangan hapus file model GGUF
  --purge-workspace     Hapus workspace
  --purge-all           Hapus seluruh /opt/gh0st-pi dan /opt/llama
  --dry-run             Tampilkan aksi, jangan ubah sistem
  -y, --yes             Tanpa konfirmasi
  --try-pi-uninstall    Coba lepas ekstensi Pi yang dipasang setup.sh
  --keep-opt-llama      Jangan sentuh /opt/llama
  --force               Izinkan hapus GH0ST_ROOT non-default tanpa state file
  -h, --help            Tampilkan bantuan

Examples:
  sudo sh uninstall.sh --dry-run
  sudo sh uninstall.sh
  sudo sh uninstall.sh --keep-models -y
  sudo sh uninstall.sh --purge-all -y
EOF
}

# ---------------------------------------------------------------------------
# Argumen
# ---------------------------------------------------------------------------
KEEP_MODELS=0
PURGE_WORKSPACE=0
PURGE_ALL=0
DRY_RUN=0
ASSUME_YES=0
REMOVE_PI_EXT=0
KEEP_OPT_LLAMA=0
FORCE=0

while [ $# -gt 0 ]; do
    case "$1" in
        --keep-models)      KEEP_MODELS=1 ;;
        --purge-workspace)  PURGE_WORKSPACE=1 ;;
        --purge-all)
            PURGE_ALL=1
            KEEP_MODELS=0
            PURGE_WORKSPACE=1
            KEEP_OPT_LLAMA=0
            ;;
        --dry-run)          DRY_RUN=1 ;;
        -y|--yes)           ASSUME_YES=1 ;;
        --try-pi-uninstall) REMOVE_PI_EXT=1 ;;
        --keep-opt-llama)   KEEP_OPT_LLAMA=1 ;;
        --force)            FORCE=1 ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            err "Opsi tidak dikenal: $1"
            ;;
    esac
    shift
done

[ "$(id -u)" -eq 0 ] || err "Skrip ini membutuhkan root. Jalankan: sudo sh uninstall.sh"

# ---------------------------------------------------------------------------
# Lokasi. Prioritas: state file yang ditulis setup.sh > environment > default.
# ---------------------------------------------------------------------------
GH0ST_ROOT="${GH0ST_ROOT:-/opt/gh0st-pi}"
OPT_LLAMA="${OPT_LLAMA:-/opt/llama}"
STATE="$GH0ST_ROOT/.gh0st-pi-state"

[ -n "$GH0ST_ROOT" ] || err "GH0ST_ROOT kosong"
[ -n "$OPT_LLAMA" ] || err "OPT_LLAMA kosong"

case "$GH0ST_ROOT" in
    /|/opt|/opt/|//|/home|/usr|/var|/etc|/root)
        err "GH0ST_ROOT terlalu berbahaya: $GH0ST_ROOT"
        ;;
esac
case "$OPT_LLAMA" in
    /|/opt|/opt/|//|/home|/usr|/var|/etc|/root)
        err "OPT_LLAMA terlalu berbahaya: $OPT_LLAMA"
        ;;
esac

# state_get KEY -> nilai (dibaca dengan sed, file TIDAK dieksekusi)
state_get() {
    sed -n "s/^$1='\(.*\)'\$/\1/p" "$STATE" 2>/dev/null | head -n 1
}

HAVE_STATE=0
if [ -f "$STATE" ]; then
    if [ "$(stat -c %u "$STATE" 2>/dev/null)" = "0" ]; then
        HAVE_STATE=1
    else
        warn "state file bukan milik root; DIABAIKAN: $STATE"
    fi
fi

if [ "$HAVE_STATE" = 0 ] && [ "$GH0ST_ROOT" != "/opt/gh0st-pi" ] && [ "$FORCE" != 1 ]; then
    err "State file tidak ada di $GH0ST_ROOT, dan lokasinya bukan default /opt/gh0st-pi. Ini bukan instalasi gh0st-pi? (--force untuk memaksa)"
fi

pick() {
    # pick KEY DEFAULT
    _v=""
    if [ "$HAVE_STATE" = 1 ]; then
        _v=$(state_get "$1")
    fi
    if [ -z "$_v" ]; then
        _v="$2"
    fi
    printf '%s' "$_v"
}

LLAMA_HOME=$(pick LLAMA_HOME "$GH0ST_ROOT/llama")
LLAMA_MODELS=$(pick LLAMA_MODELS "$GH0ST_ROOT/models")
UV_HOME=$(pick UV_HOME "$GH0ST_ROOT/uv")
HEX_DIR=$(pick HEX_DIR "$GH0ST_ROOT/tools/hexstrike-ai")
HEX_CACHE=$(pick HEX_CACHE "$GH0ST_ROOT/.cache/pip")
WORKSPACE=$(pick WORKSPACE "$GH0ST_ROOT/workspace")
SV=$(pick SV "/etc/sv/llama")
RN=$(pick RN "/etc/runit/runsvdir/default")
SVLOG_DIR=$(pick SVLOG_DIR "/var/log/llama")
BIN_DIR=$(pick BIN_DIR "/usr/local/bin")
LLAMA_USER=$(pick LLAMA_USER "_llama")
LLAMA_STATE=$(pick LLAMA_STATE "/var/lib/llama")
MODEL_FILES=$(pick MODEL_FILES "Qwen3-4B-Q4_K_M.gguf Qwen3-8B-Q4_K_M.gguf Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf")

KS_DIR="$GH0ST_ROOT/tools/kittysploit"      # varian lama
MARKER="gh0st-pi-llama-env"
PI_EXTENSIONS="pi-llama-cpp pi-agent-modes pi-themes pi-manage-todo-list pi-redteam pi-security-analysis"

# ---------------------------------------------------------------------------
# User asli saat dijalankan via sudo/doas
# ---------------------------------------------------------------------------
REAL_USER="${SUDO_USER:-${DOAS_USER:-${USER:-root}}}"
REAL_HOME=$(getent passwd "$REAL_USER" 2>/dev/null | cut -d: -f6 || true)
if [ -z "$REAL_HOME" ]; then
    REAL_HOME=$(awk -F: -v u="$REAL_USER" '$1==u {print $6; exit}' /etc/passwd 2>/dev/null || true)
fi

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
run_cmd() {
    if [ "$DRY_RUN" = 1 ]; then
        printf '%s: DRY-RUN:' "$0" >&2
        printf ' %s' "$@" >&2
        printf '\n' >&2
        return 0
    fi
    "$@"
}

is_critical_path() {
    case "$1" in
        /|/bin|/boot|/dev|/etc|/home|/lib|/lib32|/lib64|/proc|/root|/run|/sbin|/sys|/usr|/var|/opt|/mnt|/tmp)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

remove_path() {
    _p="$1"

    if [ -z "$_p" ] || is_critical_path "$_p"; then
        err "Menolak menghapus path kritis/kosong: '$_p'"
    fi
    # jangan pernah menghapus home user atau induknya
    if [ -n "$REAL_HOME" ]; then
        case "$REAL_HOME/" in
            "$_p"/*) err "Menolak menghapus path yang memuat home user: $_p" ;;
        esac
    fi

    if [ -e "$_p" ] || [ -L "$_p" ]; then
        info "Menghapus: $_p"
        run_cmd rm -rf "$_p" || true
    fi
}

# remove_symlink_matching LINK NEEDLE...  -> hapus LINK jika targetnya memuat salah satu NEEDLE
remove_symlink_matching() {
    _link="$1"
    shift

    if [ -L "$_link" ]; then
        _target=$(readlink "$_link" 2>/dev/null || true)
        for _needle in "$@"; do
            case "$_target" in
                *"$_needle"*)
                    info "Menghapus symlink: $_link -> $_target"
                    run_cmd rm -f "$_link" || true
                    return 0
                    ;;
            esac
        done
    fi
    return 0
}

# Hapus file bantu hanya jika memuat penanda 'gh0st-pi-managed' (dibuat setup.sh)
remove_managed_file() {
    if [ -f "$1" ] && grep -q "gh0st-pi-managed" "$1" 2>/dev/null; then
        info "Menghapus: $1"
        run_cmd rm -f "$1" || true
    fi
}

# Hanya baris milik gh0st-pi yang dibuang; baris lain (juga yang tepat setelah blok) AMAN.
remove_env_block() {
    _file="$1"
    _marker="$2"

    [ -f "$_file" ] || return 0

    if ! grep -q "^# ${_marker}\$" "$_file" 2>/dev/null; then
        return 0
    fi

    info "Membersihkan env block '${_marker}' dari $_file"

    if [ "$DRY_RUN" = 1 ]; then
        return 0
    fi

    _bak="$_file.gh0st-uninstall.$(date +%s).bak"
    cp -p "$_file" "$_bak" 2>/dev/null || cp "$_file" "$_bak" 2>/dev/null || true

    _tmp=$(mktemp) || {
        warn "mktemp gagal, tidak jadi membersihkan $_file"
        return 0
    }

    awk -v marker="# ${_marker}" '
        BEGIN { skip = 0 }
        skip == 0 && $0 == marker { skip = 1; next }
        skip == 1 && $0 ~ /^(export |set -gx )(LLAMA_|PI_TELEMETRY)/ { next }
        skip == 1 { skip = 0 }
        { print }
    ' "$_file" > "$_tmp" || {
        rm -f "$_tmp"
        warn "awk gagal, tidak jadi membersihkan $_file"
        return 0
    }

    cat "$_tmp" > "$_file" || {
        rm -f "$_tmp"
        warn "gagal menulis kembali $_file"
        return 0
    }

    rm -f "$_tmp"

    if [ -f "$_bak" ]; then
        info "Backup file rc disimpan di: $_bak"
    fi
}

# ---------------------------------------------------------------------------
# Konfirmasi
# ---------------------------------------------------------------------------
if [ "$DRY_RUN" != 1 ] && [ "$ASSUME_YES" != 1 ]; then
    cat >&2 <<EOF
Uninstaller gh0st-pi
(lokasi dibaca dari: $( [ "$HAVE_STATE" = 1 ] && echo "$STATE" || echo "nilai default" ))

Aksi yang akan dilakukan:
  - Mematikan & melepas service AI: $SV  (link: $RN/llama)
  - Menghapus user sistem '$LLAMA_USER', $LLAMA_STATE, dan log $SVLOG_DIR
  - Menghapus perintah bantu gh0st-ai / gh0st-hexstrike di $BIN_DIR (jika buatan setup.sh)
  - Membersihkan env block '$MARKER' dari rc user:
      $REAL_HOME/.bashrc  $REAL_HOME/.zshrc  $REAL_HOME/.config/fish/config.fish
  - Menghapus: $LLAMA_HOME, $UV_HOME, $HEX_DIR, $HEX_CACHE
EOF

    if [ "$KEEP_MODELS" = 1 ]; then
        printf '  - Model GGUF DISIMPAN: %s\n' "$LLAMA_MODELS" >&2
    else
        printf '  - Model GGUF akan DIHAPUS dari: %s\n' "$LLAMA_MODELS" >&2
    fi

    if [ "$PURGE_WORKSPACE" = 1 ]; then
        printf '  - Workspace akan DIHAPUS: %s\n' "$WORKSPACE" >&2
    else
        printf '  - Workspace DISIMPAN: %s\n' "$WORKSPACE" >&2
    fi

    if [ "$PURGE_ALL" = 1 ]; then
        printf '\nPERINGATAN: --purge-all menghapus SELURUH %s dan %s\n' "$GH0ST_ROOT" "$OPT_LLAMA" >&2
    fi

    printf '\nLanjut? [y/N] ' >&2
    read -r answer || answer=""

    case "$answer" in
        y|Y|yes|YES)
            ;;
        *)
            info "Dibatalkan oleh user."
            exit 0
            ;;
    esac
fi

# ---------------------------------------------------------------------------
# 1. Service runit  (urutan penting: matikan -> lepas link -> TUNGGU -> baru hapus direktori)
# ---------------------------------------------------------------------------
info "Melepas runit service llama..."

if have sv && [ -d "$SV" ]; then
    run_cmd sv down "$SV" || true
fi

_had_link=0
if [ -L "$RN/llama" ] || [ -e "$RN/llama" ]; then
    _had_link=1
    info "Menghapus link service: $RN/llama"
    run_cmd rm -f "$RN/llama" || true
fi

if [ "$DRY_RUN" != 1 ] && [ "$_had_link" = 1 ]; then
    info "Menunggu runsvdir melepas service..."
    sleep 6
fi

remove_path "$SV"

# user sistem + state + log (hanya jika memang akun buatan setup.sh: home-nya cocok)
_uh=$(getent passwd "$LLAMA_USER" 2>/dev/null | cut -d: -f6 || true)
if [ -n "$_uh" ] && [ "$_uh" = "$LLAMA_STATE" ]; then
    info "Menghapus user sistem: $LLAMA_USER"
    run_cmd userdel "$LLAMA_USER" || warn "userdel $LLAMA_USER gagal"
elif [ -n "$_uh" ]; then
    warn "User '$LLAMA_USER' ada tapi home-nya '$_uh' != '$LLAMA_STATE'; TIDAK dihapus."
fi
remove_path "$LLAMA_STATE"
remove_path "$SVLOG_DIR"

# ---------------------------------------------------------------------------
# 2. Symlink & perintah bantu
# ---------------------------------------------------------------------------
info "Membersihkan symlink/perintah bantu milik gh0st-pi..."

remove_symlink_matching "$BIN_DIR/llama" "$LLAMA_HOME" "$GH0ST_ROOT" "$OPT_LLAMA" ".llama-app"

# uv/uvx: HANYA yang menunjuk ke UV_HOME buatan setup (uv milik user sendiri tidak disentuh)
for b in uv uvx; do
    remove_symlink_matching "$BIN_DIR/$b" "$UV_HOME"
done

remove_managed_file "$BIN_DIR/gh0st-ai"
remove_managed_file "$BIN_DIR/gh0st-hexstrike"

# ---------------------------------------------------------------------------
# 3. Env block di shell rc user
# ---------------------------------------------------------------------------
info "Membersihkan env block dari shell rc user..."

if [ -n "$REAL_HOME" ]; then
    remove_env_block "$REAL_HOME/.bashrc" "$MARKER"
    remove_env_block "$REAL_HOME/.zshrc" "$MARKER"
    remove_env_block "$REAL_HOME/.config/fish/config.fish" "$MARKER"
else
    warn "REAL_HOME kosong untuk user '$REAL_USER'; langkah pembersihan rc dilewati."
fi

# ---------------------------------------------------------------------------
# 4. Ekstensi Pi, opsional
# ---------------------------------------------------------------------------
if [ "$REMOVE_PI_EXT" = 1 ]; then
    info "Mencoba melepas ekstensi Pi (sebagai user '$REAL_USER')..."

    _pi=$(command -v pi 2>/dev/null || true)
    if [ -z "$_pi" ] && [ -x "$REAL_HOME/.local/bin/pi" ]; then
        _pi="$REAL_HOME/.local/bin/pi"
    fi

    if [ -n "$_pi" ] && [ "$REAL_USER" != root ]; then
        for ext in $PI_EXTENSIONS; do
            info "Pi remove: $ext"
            if [ "$DRY_RUN" = 1 ]; then
                printf '%s: DRY-RUN: pi remove npm:%s\n' "$0" "$ext" >&2
                continue
            fi
            if have chpst && chpst -u "$REAL_USER" env HOME="$REAL_HOME" PATH="$(dirname "$_pi"):$PATH" \
                 PI_OFFLINE=1 "$_pi" remove "npm:$ext" < /dev/null >/dev/null 2>&1; then
                info "OK: $ext"
            else
                warn "Tidak terlepas/tidak terpasang: $ext (manual: pi remove npm:$ext)"
            fi
        done
    else
        warn "Perintah 'pi' atau user biasa tidak ditemukan. Ekstensi Pi tidak dilepas."
    fi
else
    info "Ekstensi Pi tidak dilepas otomatis. Gunakan --try-pi-uninstall jika perlu."
fi

# ---------------------------------------------------------------------------
# 5. Artefak disk
# ---------------------------------------------------------------------------

# Model: hanya file yang dikenal (dari state), bukan seluruh folder -- aman utk folder model custom
if [ "$KEEP_MODELS" = 0 ]; then
    for f in $MODEL_FILES; do
        case "$f" in
            */*|"") continue ;;
        esac
        for suffix in "" ".part"; do
            if [ -e "$LLAMA_MODELS/$f$suffix" ]; then
                info "Menghapus model: $LLAMA_MODELS/$f$suffix"
                run_cmd rm -f "$LLAMA_MODELS/$f$suffix" || true
            fi
        done
    done
    if [ "$DRY_RUN" != 1 ] && [ -d "$LLAMA_MODELS" ]; then
        rmdir "$LLAMA_MODELS" 2>/dev/null || info "Folder model tidak kosong (ada file lain), dibiarkan: $LLAMA_MODELS"
    fi
    if [ -d "$OPT_LLAMA/models" ]; then
        remove_path "$OPT_LLAMA/models"
    fi
else
    info "Menyimpan model GGUF: $LLAMA_MODELS"
fi

if [ "$PURGE_ALL" = 1 ]; then
    info "Purge all: menghapus seluruh root instalasi..."
    remove_path "$GH0ST_ROOT"
    remove_path "$OPT_LLAMA"
else
    info "Membersihkan artefak gh0st-pi secara selektif..."

    remove_path "$LLAMA_HOME"
    remove_path "$UV_HOME"
    remove_path "$HEX_DIR"
    remove_path "$KS_DIR"
    remove_path "$HEX_CACHE"
    remove_path "$GH0ST_ROOT/tools/hexstrike_local.py"

    if [ "$KEEP_OPT_LLAMA" = 0 ]; then
        for d in bin lib src include; do
            remove_path "$OPT_LLAMA/$d"
        done
        if [ "$DRY_RUN" != 1 ]; then
            rmdir "$OPT_LLAMA" 2>/dev/null || true
        fi
    else
        info "Menyimpan $OPT_LLAMA sesuai --keep-opt-llama"
    fi

    if [ "$PURGE_WORKSPACE" = 1 ]; then
        remove_path "$WORKSPACE"
    elif [ -d "$WORKSPACE" ]; then
        info "Menyimpan workspace: $WORKSPACE"
    fi

    # rapikan direktori kosong; state file ikut dihapus HANYA bila tak ada lagi yang tersisa
    if [ "$DRY_RUN" != 1 ]; then
        for d in "$GH0ST_ROOT/tools" "$GH0ST_ROOT/.cache"; do
            [ -d "$d" ] && rmdir "$d" 2>/dev/null || true
        done
        _left=""
        for _e in "$GH0ST_ROOT"/* "$GH0ST_ROOT"/.[!.]*; do
            if [ -e "$_e" ] && [ "$_e" != "$STATE" ]; then
                _left="ada"
            fi
        done
        if [ -d "$GH0ST_ROOT" ] && [ -z "$_left" ]; then
            rm -f "$STATE"
            rmdir "$GH0ST_ROOT" 2>/dev/null || true
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Final message
# ---------------------------------------------------------------------------
info "Uninstall gh0st-pi selesai."

if [ "$DRY_RUN" = 1 ]; then
    info "Ini hanya dry-run. Tidak ada perubahan nyata yang dilakukan."
fi

if [ "$KEEP_MODELS" = 1 ] && [ "$PURGE_ALL" != 1 ]; then
    info "Model GGUF masih tersimpan di: $LLAMA_MODELS"
fi

if [ "$PURGE_WORKSPACE" != 1 ] && [ "$PURGE_ALL" != 1 ] && [ -d "$WORKSPACE" ]; then
    info "Workspace masih tersimpan di: $WORKSPACE"
fi

if [ -n "$REAL_HOME" ]; then
    info "Buka shell baru agar env lama hilang."
fi

info "Catatan:"
info "  - Pi (dan symlink $BIN_DIR/pi) tidak dihapus; ~/.pi milik user tidak dihapus."
info "  - Tool eksternal seperti nmap, gobuster, sqlmap, dll. tidak dihapus."
info "  - Hapus Pi manual bila mau: npm uninstall -g --prefix ~/.local @earendil-works/pi-coding-agent"
