#!/usr/bin/env python3
"""
HexStrike AI - Advanced Penetration Testing Framework Server
Entry point - semua logic ada di package hexstrike/
"""
import argparse
from hexstrike.config import API_PORT, API_HOST
from hexstrike.core.visual_engine import ModernVisualEngine
from hexstrike.core.logging import setup_logging
from hexstrike.api.app import create_app

def main():
    parser = argparse.ArgumentParser(description="Run the HexStrike AI API Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--port", type=int, default=API_PORT, help=f"Port (default: {API_PORT})")
    args = parser.parse_args()

    setup_logging(debug=args.debug)
    print(ModernVisualEngine.create_banner())

    app = create_app(debug=args.debug)
    # JANGAN "0.0.0.0": /api/command menjalankan perintah shell tanpa autentikasi. Default API_HOST = 127.0.0.1.
    app.run(host=API_HOST, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()