#!/usr/bin/env bash
# Start HexStrike MCP Client dengan uv
set -euo pipefail
cd "$(dirname "$0")/.."

SERVER_URL="${1:-http://127.0.0.1:8888}"

if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment belum dibuat. Jalankan ./setup.sh dulu"
    exit 1
fi

echo "🔌 Connecting to HexStrike Server at $SERVER_URL..."
exec uv run python hexstrike_mcp.py --server "$SERVER_URL"