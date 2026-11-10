"""
HexStrike AI - MCP Cloud Security Tools
"""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


def register_tools(mcp: FastMCP, client: HexStrikeClient):

    @mcp.tool()
    def prowler_scan(provider: str = "aws", profile: str = "default",
                     region: str = "", checks: str = "") -> Dict[str, Any]:
        """Execute Prowler for cloud security assessment."""
        data = {"provider": provider, "profile": profile, "region": region, "checks": checks}
        logger.info(f"☁️ Prowler {provider} assessment")
        return client.safe_post("api/tools/prowler", data)

    @mcp.tool()
    def trivy_scan(scan_type: str = "image", target: str = "",
                   severity: str = "") -> Dict[str, Any]:
        """Execute Trivy for container vulnerability scanning."""
        data = {"scan_type": scan_type, "target": target, "severity": severity}
        logger.info(f"🔍 Trivy {scan_type}: {target}")
        return client.safe_post("api/tools/trivy", data)

    @mcp.tool()
    def scout_suite_assessment(provider: str = "aws",
                               profile: str = "default") -> Dict[str, Any]:
        """Execute Scout Suite for multi-cloud assessment."""
        data = {"provider": provider, "profile": profile}
        logger.info(f"☁️ Scout Suite {provider}")
        return client.safe_post("api/tools/scout-suite", data)

    @mcp.tool()
    def kube_hunter_scan(target: str = "", active: bool = False) -> Dict[str, Any]:
        """Execute kube-hunter for Kubernetes penetration testing."""
        data = {"target": target, "active": active}
        logger.info("☁️ kube-hunter scan")
        return client.safe_post("api/tools/kube-hunter", data)

    @mcp.tool()
    def kube_bench_cis(targets: str = "") -> Dict[str, Any]:
        """Execute kube-bench for CIS Kubernetes benchmarks."""
        data = {"targets": targets}
        logger.info("☁️ kube-bench CIS benchmark")
        return client.safe_post("api/tools/kube-bench", data)

    @mcp.tool()
    def docker_bench_security_scan(checks: str = "") -> Dict[str, Any]:
        """Execute Docker Bench for Security."""
        data = {"checks": checks}
        logger.info("🐳 Docker Bench Security")
        return client.safe_post("api/tools/docker-bench-security", data)

    @mcp.tool()
    def checkov_iac_scan(directory: str = ".", framework: str = "") -> Dict[str, Any]:
        """Execute Checkov for IaC security scanning."""
        data = {"directory": directory, "framework": framework}
        logger.info(f"🔍 Checkov IaC: {directory}")
        return client.safe_post("api/tools/checkov", data)

    @mcp.tool()
    def terrascan_iac_scan(scan_type: str = "all", iac_dir: str = ".") -> Dict[str, Any]:
        """Execute Terrascan for IaC security scanning."""
        data = {"scan_type": scan_type, "iac_dir": iac_dir}
        logger.info(f"🔍 Terrascan: {iac_dir}")
        return client.safe_post("api/tools/terrascan", data)

    @mcp.tool()
    def clair_vulnerability_scan(image: str) -> Dict[str, Any]:
        """Execute Clair for container vulnerability analysis."""
        data = {"image": image}
        logger.info(f"🐳 Clair: {image}")
        return client.safe_post("api/tools/clair", data)

    @mcp.tool()
    def falco_runtime_monitoring(duration: int = 60) -> Dict[str, Any]:
        """Execute Falco for runtime security monitoring."""
        data = {"duration": duration}
        logger.info(f"🛡️ Falco monitoring for {duration}s")
        return client.safe_post("api/tools/falco", data)