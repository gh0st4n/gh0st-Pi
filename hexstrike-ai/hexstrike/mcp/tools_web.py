"""
HexStrike AI - MCP Web Security Tools
"""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.core.colors import HexStrikeColors as C
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


def register_tools(mcp: FastMCP, client: HexStrikeClient):
    """Register semua web security tools."""

    @mcp.tool()
    def gobuster_scan(url: str, mode: str = "dir", wordlist: str = "/usr/share/wordlists/dirb/common.txt") -> Dict[str, Any]:
        """Execute Gobuster directory/DNS/vhost scan."""
        data = {"url": url, "mode": mode, "wordlist": wordlist, "use_recovery": True}
        logger.info(f"{C.CRIMSON}📁 Gobuster {mode}: {url}{C.RESET}")
        return client.safe_post("api/tools/gobuster", data)

    @mcp.tool()
    def nuclei_scan(target: str, severity: str = "", tags: str = "") -> Dict[str, Any]:
        """Execute Nuclei vulnerability scanner."""
        data = {"target": target, "severity": severity, "tags": tags, "use_recovery": True}
        logger.info(f"{C.BLOOD_RED}🔬 Nuclei: {target}{C.RESET}")
        return client.safe_post("api/tools/nuclei", data)

    @mcp.tool()
    def sqlmap_scan(url: str, data: str = "", additional_args: str = "") -> Dict[str, Any]:
        """Execute SQLMap SQL injection testing."""
        data_payload = {"url": url, "data": data, "additional_args": additional_args}
        logger.info(f"💉 SQLMap: {url}")
        return client.safe_post("api/tools/sqlmap", data_payload)

    @mcp.tool()
    def ffuf_scan(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt", mode: str = "directory") -> Dict[str, Any]:
        """Execute FFuf web fuzzing."""
        data = {"url": url, "wordlist": wordlist, "mode": mode}
        return client.safe_post("api/tools/ffuf", data)

    # ... tool lainnya: feroxbuster, dirsearch, katana, gau, waybackurls,
    #     arjun, paramspider, x8, dalfox, httpx, nikto, wpscan, wafw00f