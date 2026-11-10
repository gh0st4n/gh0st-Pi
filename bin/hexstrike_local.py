#!/usr/bin/env python3
"""Peluncur HexStrike yang HANYA mendengarkan di 127.0.0.1.

Mengapa ada: server upstream memanggil app.run(host="0.0.0.0") (variabel HEXSTRIKE_HOST
dibaca tapi tidak dipakai untuk bind), dan endpoint /api/command mengeksekusi perintah shell
tanpa autentikasi. Dijalankan langsung, siapa pun di jaringan yang sama (WiFi/LAN) bisa
menjalankan perintah di mesin ini. Peluncur ini mengimpor 'app' lalu menjalankannya sendiri
dengan host yang benar. Source upstream TIDAK diubah.
"""
import argparse
import os
import sys


def main():
    hex_dir = os.environ.get("HEX_DIR", "")
    if not hex_dir or not os.path.isfile(os.path.join(hex_dir, "hexstrike_server.py")):
        sys.exit("[gh0st-pi] HEX_DIR tidak valid (hexstrike_server.py tidak ditemukan). "
                 "Jalankan lewat 'gh0st-hexstrike'.")

    parser = argparse.ArgumentParser(description="HexStrike (localhost only)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("HEXSTRIKE_PORT", "8888")))
    args = parser.parse_args()

    sys.path.insert(0, hex_dir)
    os.chdir(hex_dir)
    import hexstrike_server as hs  # noqa: E402  (import menjalankan inisialisasi modul, bukan server)

    if not hasattr(hs, "app"):
        sys.exit("[gh0st-pi] struktur upstream berubah (objek 'app' tidak ada). "
                 "JANGAN jalankan hexstrike_server.py langsung: bind-nya 0.0.0.0 tanpa autentikasi.")

    print("[gh0st-pi] HexStrike hanya di http://127.0.0.1:%d (debug dimatikan)" % args.port, flush=True)
    hs.app.run(host="127.0.0.1", port=args.port, debug=False)


if __name__ == "__main__":
    main()

