#!/usr/bin/env bash
# Cleanup environment
set -euo pipefail

echo "🧹 Cleaning up HexStrike AI environment..."

# Hapus cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage

# Hapus temp files
rm -rf /tmp/hexstrike_* /tmp/prowler_* /tmp/scout-suite_* 2>/dev/null || true

# Optional: hapus venv
read -p "Hapus virtual environment juga? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf .venv
    echo "✅ Virtual environment dihapus"
fi

echo "✅ Cleanup selesai"