#!/usr/bin/env python3
"""Peluncur HexStrike yang HANYA mendengarkan di 127.0.0.1.

Mengapa ada: server HexStrike (upstream DAN refactor modular) memanggil app.run(host="0.0.0.0", ...).
Variabel HEXSTRIKE_HOST / API_HOST dibaca tetapi tidak dipakai untuk bind, dan endpoint
POST /api/command mengeksekusi perintah shell tanpa autentikasi. Dijalankan langsung, siapa pun
di jaringan yang sama (WiFi/LAN) bisa menjalankan perintah di mesin ini. Opsi --debug lebih buruk
lagi: debugger Werkzeug di semua antarmuka = eksekusi kode.

Peluncur ini membuat objek Flask 'app' sendiri lalu menjalankannya dengan host yang benar.
Dua layout didukung; source HexStrike TIDAK diubah:
  1. modular : hexstrike/api/app.py dengan factory create_app()
  2. satu-file upstream : objek 'app' di hexstrike_server.py
"""
import argparse
import os
import sys


def load_app(hex_dir):
    sys.path.insert(0, hex_dir)
    os.chdir(hex_dir)

    if os.path.isfile(os.path.join(hex_dir, "hexstrike", "api", "app.py")):
        try:
            from hexstrike.core.logging import setup_logging
            setup_logging(debug=False)
        except Exception:  # logging bukan syarat untuk menyalakan app
            pass
        from hexstrike.api.app import create_app
        return create_app(debug=False)

    import hexstrike_server as hs  # noqa: E402  (import menjalankan inisialisasi modul, bukan server)
    if hasattr(hs, "app"):
        return hs.app

    sys.exit("[gh0st-pi] struktur HexStrike tidak dikenali (tidak ada hexstrike/api/app.py maupun objek 'app'). "
             "JANGAN jalankan hexstrike_server.py langsung: bind-nya 0.0.0.0 tanpa autentikasi.")


def main():
    hex_dir = os.environ.get("HEX_DIR", "")
    if not hex_dir or not os.path.isfile(os.path.join(hex_dir, "hexstrike_server.py")):
        sys.exit("[gh0st-pi] HEX_DIR tidak valid (hexstrike_server.py tidak ditemukan). "
                 "Jalankan lewat 'gh0st-hexstrike'.")

    parser = argparse.ArgumentParser(description="HexStrike (localhost only)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("HEXSTRIKE_PORT", "8888")))
    args = parser.parse_args()

    app = load_app(hex_dir)
    print("[gh0st-pi] HexStrike hanya di http://127.0.0.1:%d (debug dimatikan)" % args.port, flush=True)
    app.run(host="127.0.0.1", port=args.port, debug=False)


if __name__ == "__main__":
    main()
