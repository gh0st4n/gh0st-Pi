#!/usr/bin/env bash
# Start HexStrike Server dengan uv
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment belum dibuat. Jalankan ./setup.sh dulu"
    exit 1
fi

echo "🚀 Starting HexStrike AI Server..."
exec uv run python hexstrike_server.py "$@"