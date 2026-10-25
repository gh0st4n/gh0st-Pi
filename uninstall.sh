#!/bin/sh
# uninstall.sh - Uninstaller untuk gh0st-Pi / gh0st-pi
#
# Mendukung varian setup.sh:
#   1) gh0st-pi  : llama.app resmi + HexStrike AI
#   2) gh0st-Pi  : build /opt/llama + KittySploit
#
# Prinsip:
#   - Melepas service runit llama
#   - Membersihkan artefak instalasi gh0st-Pi
#   - Membersihkan env block di rc shell user
#   - Tidak menghapus Pi core, ~/.pi, tool eksternal, atau workspace tanpa diminta
#
# Usage:
#   sudo sh uninstall.sh [options]
#
# Options:
#   --keep-models         Jangan hapus direktori model GGUF
#   --purge-workspace     Hapus /opt/gh0st-pi/workspace
#   --purge-all           Hapus seluruh /opt/gh0st-pi dan /opt/llama
#   --dry-run             Tampilkan aksi, jangan ubah sistem
#   -y, --yes             Tanpa konfirmasi
#   --try-pi-uninstall    Coba lepas ekstensi Pi yang pernah di-install setup.sh
#   --keep-opt-llama      Jangan sentuh /opt/llama
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
  --keep-models         Jangan hapus direktori model GGUF
  --purge-workspace     Hapus /opt/gh0st-pi/workspace
  --purge-all           Hapus seluruh /opt/gh0st-pi dan /opt/llama
  --dry-run             Tampilkan aksi, jangan ubah sistem
  -y, --yes             Tanpa konfirmasi
  --try-pi-uninstall    Coba lepas ekstensi Pi yang pernah di-install setup.sh
  --keep-opt-llama      Jangan sentuh /opt/llama
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

while [ $# -gt 0 ]; do
    case "$1" in
        --keep-models)
            KEEP_MODELS=1
            ;;
        --purge-workspace)
            PURGE_WORKSPACE=1
            ;;
        --purge-all)
            PURGE_ALL=1
            KEEP_MODELS=0
            PURGE_WORKSPACE=1
            KEEP_OPT_LLAMA=0
            ;;
        --dry-run)
            DRY_RUN=1
            ;;
        -y|--yes)
            ASSUME_YES=1
            ;;
        --try-pi-uninstall)
            REMOVE_PI_EXT=1
            ;;
        --keep-opt-llama)
            KEEP_OPT_LLAMA=1
            ;;
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

# ---------------------------------------------------------------------------
# Root check
# ---------------------------------------------------------------------------
[ "$(id -u)" -eq 0 ] || err "Skrip ini membutuhkan root. Jalankan: sudo sh uninstall.sh"

# ---------------------------------------------------------------------------
# Konfigurasi path
# ---------------------------------------------------------------------------
GH0ST_ROOT="${GH0ST_ROOT:-/opt/gh0st-pi}"
OPT_LLAMA="${OPT_LLAMA:-/opt/llama}"
SV="${SV:-/etc/sv/llama}"
RN="${RN:-/etc/runit/runsvdir/default}"

LLAMA_HOME="$GH0ST_ROOT/llama"
LLAMA_MODELS="$GH0ST_ROOT/models"
UV_HOME="$GH0ST_ROOT/uv"
HEX_DIR="$GH0ST_ROOT/tools/hexstrike-ai"
KS_DIR="$GH0ST_ROOT/tools/kittysploit"
WORKSPACE="$GH0ST_ROOT/workspace"

MARKER="gh0st-pi-llama-env"

# Ekstensi Pi yang pernah dicoba di-install oleh setup.sh varian HexStrike.
# Varian KittySploit hanya memakai pi-llama-cpp, tapi daftar ini tetap aman.
PI_EXTENSIONS="pi-llama-cpp pi-agent-modes pi-themes pi-manage-todo-list pi-redteam pi-security-analysis"

# Guard sederhana agar tidak salah hapus path kritis karena env override.
[ -n "$GH0ST_ROOT" ] || err "GH0ST_ROOT kosong"
[ -n "$OPT_LLAMA" ] || err "OPT_LLAMA kosong"

case "$GH0ST_ROOT" in
    /|/opt|/opt/|//)
        err "GH0ST_ROOT terlalu berbahaya: $GH0ST_ROOT"
        ;;
esac

case "$OPT_LLAMA" in
    /|/opt|/opt/|//)
        err "OPT_LLAMA terlalu berbahaya: $OPT_LLAMA"
        ;;
esac

# ---------------------------------------------------------------------------
# Resolve user asli saat dijalankan via sudo
# ---------------------------------------------------------------------------
REAL_USER="${SUDO_USER:-${USER:-root}}"
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
        /|/bin|/boot|/dev|/etc|/home|/lib|/lib32|/lib64|/proc|/root|/run|/sbin|/sys|/usr|/var)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

remove_path() {
    _p="$1"

    if is_critical_path "$_p"; then
        err "Menolak menghapus path kritis: $_p"
    fi

    if [ -e "$_p" ] || [ -L "$_p" ]; then
        info "Menghapus: $_p"
        run_cmd rm -rf "$_p" || true
    fi
}

remove_symlink_matching() {
    _link="$1"
    _needle="$2"

    if [ -L "$_link" ]; then
        _target=$(readlink "$_link" 2>/dev/null || true)
        case "$_target" in
            *"$_needle"*)
                info "Menghapus symlink: $_link -> $_target"
                run_cmd rm -f "$_link" || true
                ;;
        esac
    fi
}

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
        $0 == marker { skip = 1; next }
        skip == 1 && $0 == "" { skip = 0; next }
        skip == 1 { next }
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
    chown "$REAL_USER" "$_file" 2>/dev/null || true

    if [ -f "$_bak" ]; then
        info "Backup file rc disimpan di: $_bak"
    fi
}

# ---------------------------------------------------------------------------
# Konfirmasi
# ---------------------------------------------------------------------------
if [ "$DRY_RUN" != 1 ] && [ "$ASSUME_YES" != 1 ]; then
    cat >&2 <<EOF
Uninstaller gh0st-Pi / gh0st-pi

Aksi yang akan dilakukan:
  - Melepas runit service: $SV dan link di $RN/llama
  - Membersihkan symlink global jika mengarah ke artefak gh0st-Pi
  - Membersihkan env block '$MARKER' dari rc user:
      $REAL_HOME/.bashrc
      $REAL_HOME/.zshrc
      $REAL_HOME/.config/fish/config.fish
  - Menghapus artefak instalasi:
      $LLAMA_HOME
      $UV_HOME
      $HEX_DIR
      $KS_DIR
      $GH0ST_ROOT/.cache/pip
EOF

    if [ "$KEEP_MODELS" = 1 ]; then
        cat >&2 <<EOF
  - Model GGUF DISIMPAN:
      $LLAMA_MODELS
      $OPT_LLAMA/models
EOF
    else
        cat >&2 <<EOF
  - Model GGUF akan DIHAPUS:
      $LLAMA_MODELS
      $OPT_LLAMA/models
EOF
    fi

    if [ "$PURGE_WORKSPACE" = 1 ]; then
        cat >&2 <<EOF
  - Workspace akan DIHAPUS:
      $WORKSPACE
EOF
    else
        cat >&2 <<EOF
  - Workspace DISIMPAN secara default:
      $WORKSPACE
EOF
    fi

    if [ "$KEEP_OPT_LLAMA" = 1 ]; then
        cat >&2 <<EOF
  - /opt/llama DISIMPAN
EOF
    else
        cat >&2 <<EOF
  - Komponen known di /opt/llama akan dibersihkan:
      $OPT_LLAMA/bin
      $OPT_LLAMA/lib
      $OPT_LLAMA/src
      $OPT_LLAMA/include
EOF
    fi

    if [ "$PURGE_ALL" = 1 ]; then
        cat >&2 <<EOF

PERINGATAN: --purge-all aktif.
Ini akan menghapus seluruh:
  $GH0ST_ROOT
  $OPT_LLAMA
EOF
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
# 1. Service runit
# ---------------------------------------------------------------------------
info "Melepas runit service llama..."

if have sv; then
    run_cmd sv stop llama || true
fi

if [ -L "$RN/llama" ] || [ -e "$RN/llama" ]; then
    info "Menghapus link service: $RN/llama"
    run_cmd rm -f "$RN/llama" || true
fi

remove_path "$SV"

if [ "$DRY_RUN" != 1 ]; then
    info "Menunggu runsvdir melepas service..."
    sleep 2
fi

# ---------------------------------------------------------------------------
# 2. Symlink global
# ---------------------------------------------------------------------------
info "Membersihkan symlink global jika milik gh0st-Pi..."

# llama
remove_symlink_matching /usr/local/bin/llama "$GH0ST_ROOT"
remove_symlink_matching /usr/local/bin/llama "$OPT_LLAMA"
remove_symlink_matching /usr/local/bin/llama ".llama-app"

# uv / uvx
for b in uv uvx; do
    remove_symlink_matching "/usr/local/bin/$b" "$UV_HOME"
    remove_symlink_matching "/usr/local/bin/$b" "/root/.local/bin"
    if [ -n "$REAL_HOME" ]; then
        remove_symlink_matching "/usr/local/bin/$b" "$REAL_HOME/.local/bin"
    fi
done

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
    info "Mencoba melepas ekstensi Pi..."

    if have pi; then
        for ext in $PI_EXTENSIONS; do
            info "Pi uninstall: $ext"
            if [ "$DRY_RUN" = 1 ]; then
                printf '%s: DRY-RUN: pi uninstall npm:%s\n' "$0" "$ext" >&2
                continue
            fi

            if pi uninstall "npm:$ext" >/dev/null 2>&1; then
                info "OK: $ext"
            elif pi remove "npm:$ext" >/dev/null 2>&1; then
                info "OK via remove: $ext"
            else
                warn "Gagal melepas $ext. Mungkin perlu manual: pi uninstall npm:$ext"
            fi
        done
    else
        warn "Perintah 'pi' tidak ditemukan. Ekstensi Pi tidak dilepas."
    fi
else
    info "Ekstensi Pi tidak dilepas otomatis. Gunakan --try-pi-uninstall jika perlu."
fi

# ---------------------------------------------------------------------------
# 5. Artefak disk
# ---------------------------------------------------------------------------
if [ "$PURGE_ALL" = 1 ]; then
    info "Purge all: menghapus seluruh root instalasi..."
    remove_path "$GH0ST_ROOT"
    remove_path "$OPT_LLAMA"
else
    info "Membersihkan artefak gh0st-Pi secara selektif..."

    # Models
    if [ "$KEEP_MODELS" = 0 ]; then
        remove_path "$LLAMA_MODELS"
        remove_path "$OPT_LLAMA/models"
    else
        info "Menyimpan model GGUF: $LLAMA_MODELS dan/atau $OPT_LLAMA/models"
    fi

    # llama.app HOME override
    remove_path "$LLAMA_HOME"

    # uv lokal di /opt
    remove_path "$UV_HOME"

    # HexStrike AI
    remove_path "$HEX_DIR"

    # KittySploit
    remove_path "$KS_DIR"

    # pip cache yang diarahkan setup.sh ke /opt
    remove_path "$GH0ST_ROOT/.cache/pip"

    # /opt/llama varian build-from-source
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

    # Workspace
    if [ "$PURGE_WORKSPACE" = 1 ]; then
        remove_path "$WORKSPACE"
    else
        if [ -d "$WORKSPACE" ]; then
            info "Menyimpan workspace: $WORKSPACE"
        fi
    fi

    # Bersihkan direktori kosong milik gh0st-Pi jika memang kosong
    for d in "$GH0ST_ROOT/tools" "$GH0ST_ROOT/.cache" "$GH0ST_ROOT"; do
        if [ -d "$d" ]; then
            run_cmd rmdir "$d" || true
        fi
    done
fi

# ---------------------------------------------------------------------------
# Final message
# ---------------------------------------------------------------------------
info "Uninstall gh0st-Pi selesai."

if [ "$DRY_RUN" = 1 ]; then
    info "Ini hanya dry-run. Tidak ada perubahan nyata yang dilakukan."
fi

if [ "$KEEP_MODELS" = 1 ] && [ "$PURGE_ALL" != 1 ]; then
    info "Model GGUF masih tersimpan. Hapus manual jika tidak diperlukan:"
    info "  sudo rm -rf $LLAMA_MODELS"
    info "  sudo rm -rf $OPT_LLAMA/models"
fi

if [ "$PURGE_WORKSPACE" != 1 ] && [ "$PURGE_ALL" != 1 ] && [ -d "$WORKSPACE" ]; then
    info "Workspace masih tersimpan di: $WORKSPACE"
    info "Hapus manual jika tidak diperlukan:"
    info "  sudo rm -rf $WORKSPACE"
fi

if [ -n "$REAL_HOME" ]; then
    info "Buka shell baru, atau reload rc manually, contoh:"
    info "  source $REAL_HOME/.bashrc"
    info "  source $REAL_HOME/.zshrc"
    info "  source $REAL_HOME/.config/fish/config.fish"
fi

info "Catatan:"
info "  - Pi core tidak dihapus."
info "  - ~/.pi milik user tidak dihapus."
info "  - Tool eksternal seperti nmap, gobuster, sqlmap, hydra, dll. tidak dihapus."
info "  - Jika ekstensi Pi masih tertinggal, cek manual dengan perintah 'pi'."