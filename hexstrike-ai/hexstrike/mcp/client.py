"""
HexStrike AI - MCP HTTP Client
"""
import time
import requests
import logging
from typing import Dict, Any, Optional

from hexstrike.config import MAX_RETRIES, DEFAULT_REQUEST_TIMEOUT
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


class HexStrikeClient:
    """Client untuk komunikasi dengan HexStrike API Server."""

    def __init__(self, server_url: str, timeout: int = DEFAULT_REQUEST_TIMEOUT):
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self._connect()

    def _connect(self):
        connected = False
        for i in range(MAX_RETRIES):
            try:
                resp = self.session.get(f"{self.server_url}/health", timeout=5)
                resp.raise_for_status()
                health = resp.json()
                connected = True
                logger.info(f"🎯 Connected to HexStrike AI at {self.server_url}")
                logger.info(f"🏥 Status: {health.get('status', 'unknown')}")
                break
            except requests.exceptions.ConnectionError:
                logger.warning(f"🔌 Connection refused (attempt {i+1})")
                time.sleep(2)
            except Exception as e:
                logger.warning(f"⚠️ Connection failed: {str(e)}")
                time.sleep(2)

        if not connected:
            logger.error(f"Failed to connect after {MAX_RETRIES} attempts")

    def safe_get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.server_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params or {}, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}", "success": False}

    def safe_post(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.server_url}/{endpoint}"
        try:
            response = self.session.post(url, json=json_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}", "success": False}

    def execute_command(self, command: str, use_cache: bool = True) -> Dict[str, Any]:
        return self.safe_post("api/command", {"command": command, "use_cache": use_cache})

    def check_health(self) -> Dict[str, Any]:
        return self.safe_get("health")