"""
HexStrike AI - Central Configuration
Semua konstanta dan konfigurasi di satu tempat.
"""
import os

# Server
API_PORT = int(os.environ.get('HEXSTRIKE_PORT', 8888))
API_HOST = os.environ.get('HEXSTRIKE_HOST', '127.0.0.1')
DEBUG_MODE = os.environ.get("DEBUG_MODE", "0").lower() in ("1", "true", "yes")

# MCP Client
DEFAULT_HEXSTRIKE_SERVER = "http://127.0.0.1:8888"
DEFAULT_REQUEST_TIMEOUT = 300
MAX_RETRIES = 3

# Command Execution
COMMAND_TIMEOUT = 300

# Cache
CACHE_SIZE = 1000
CACHE_TTL = 3600

# Process Pool
POOL_MIN_WORKERS = 4
POOL_MAX_WORKERS = 32

# Resource Thresholds
RESOURCE_THRESHOLDS = {
    "cpu_high": 85.0,
    "memory_high": 90.0,
    "disk_high": 95.0,
    "load_high": 0.8,
}

# File Operations
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
FILE_BASE_DIR = "/tmp/hexstrike_files"
ENV_BASE_DIR = "/tmp/hexstrike_envs"