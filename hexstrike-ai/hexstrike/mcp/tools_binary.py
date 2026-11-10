"""
HexStrike AI - MCP Binary Analysis Tools
"""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


def register_tools(mcp: FastMCP, client: HexStrikeClient):

    @mcp.tool()
    def gdb_analyze(binary: str, commands: str = "") -> Dict[str, Any]:
        """Execute GDB for binary analysis and debugging."""
        data = {"binary": binary, "commands": commands}
        logger.info(f"🔧 GDB analysis: {binary}")
        return client.safe_post("api/tools/gdb", data)

    @mcp.tool()
    def radare2_analyze(binary: str, commands: str = "") -> Dict[str, Any]:
        """Execute Radare2 for reverse engineering."""
        data = {"binary": binary, "commands": commands}
        logger.info(f"🔧 Radare2 analysis: {binary}")
        return client.safe_post("api/tools/radare2", data)

    @mcp.tool()
    def binwalk_analyze(file_path: str, extract: bool = False) -> Dict[str, Any]:
        """Execute Binwalk for firmware analysis."""
        data = {"file_path": file_path, "extract": extract}
        logger.info(f"🔧 Binwalk: {file_path}")
        return client.safe_post("api/tools/binwalk", data)

    @mcp.tool()
    def ropgadget_search(binary: str, gadget_type: str = "") -> Dict[str, Any]:
        """Search for ROP gadgets in a binary."""
        data = {"binary": binary, "gadget_type": gadget_type}
        logger.info(f"🔧 ROPgadget: {binary}")
        return client.safe_post("api/tools/ropgadget", data)

    @mcp.tool()
    def checksec_analyze(binary: str) -> Dict[str, Any]:
        """Check security features of a binary."""
        data = {"binary": binary}
        logger.info(f"🔧 Checksec: {binary}")
        return client.safe_post("api/tools/checksec", data)

    @mcp.tool()
    def strings_extract(file_path: str, min_len: int = 4) -> Dict[str, Any]:
        """Extract strings from a binary file."""
        data = {"file_path": file_path, "min_len": min_len}
        logger.info(f"🔧 Strings: {file_path}")
        return client.safe_post("api/tools/strings", data)

    @mcp.tool()
    def objdump_analyze(binary: str, disassemble: bool = True) -> Dict[str, Any]:
        """Analyze a binary using objdump."""
        data = {"binary": binary, "disassemble": disassemble}
        logger.info(f"🔧 Objdump: {binary}")
        return client.safe_post("api/tools/objdump", data)

    @mcp.tool()
    def ghidra_analysis(binary: str, project_name: str = "hexstrike_analysis") -> Dict[str, Any]:
        """Execute Ghidra for advanced binary analysis."""
        data = {"binary": binary, "project_name": project_name}
        logger.info(f"🔧 Ghidra: {binary}")
        return client.safe_post("api/tools/ghidra", data)

    @mcp.tool()
    def xxd_hexdump(file_path: str, offset: str = "0", length: str = "") -> Dict[str, Any]:
        """Create a hex dump of a file."""
        data = {"file_path": file_path, "offset": offset, "length": length}
        logger.info(f"🔧 XXD: {file_path}")
        return client.safe_post("api/tools/xxd", data)