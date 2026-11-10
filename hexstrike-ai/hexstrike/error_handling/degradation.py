"""
HexStrike AI - Graceful Degradation
"""
import socket
import logging
from datetime import datetime
from typing import Dict, Any, List, Set

import requests

logger = logging.getLogger(__name__)


class GracefulDegradation:
    """Ensure system continues operating even with partial tool failures."""

    def __init__(self):
        self.fallback_chains = {
            "network_discovery": [
                ["nmap", "rustscan", "masscan"],
                ["rustscan", "nmap"],
                ["ping", "telnet"],
            ],
            "web_discovery": [
                ["gobuster", "feroxbuster", "dirsearch"],
                ["feroxbuster", "ffuf"],
                ["curl", "wget"],
            ],
            "vulnerability_scanning": [
                ["nuclei", "jaeles", "nikto"],
                ["nikto", "w3af"],
                ["curl"],
            ],
            "subdomain_enumeration": [
                ["subfinder", "amass", "assetfinder"],
                ["amass", "findomain"],
                ["dig", "nslookup"],
            ],
            "parameter_discovery": [
                ["arjun", "paramspider", "x8"],
                ["ffuf", "wfuzz"],
                ["manual_testing"],
            ],
        }
        self.critical_operations: Set[str] = {
            "network_discovery", "web_discovery",
            "vulnerability_scanning", "subdomain_enumeration",
        }

    def create_fallback_chain(self, operation: str, failed_tools: List[str] = None) -> List[str]:
        if failed_tools is None:
            failed_tools = []
        chains = self.fallback_chains.get(operation, [])
        for chain in chains:
            viable = [t for t in chain if t not in failed_tools]
            if viable:
                logger.info(f"🔄 Fallback chain for {operation}: {viable}")
                return viable
        basic = {
            "network_discovery": ["ping"], "web_discovery": ["curl"],
            "vulnerability_scanning": ["curl"], "subdomain_enumeration": ["dig"],
        }
        fallback = basic.get(operation, ["manual_testing"])
        logger.warning(f"⚠️ Using basic fallback for {operation}: {fallback}")
        return fallback

    def handle_partial_failure(self, operation: str, partial_results: Dict[str, Any],
                               failed_components: List[str]) -> Dict[str, Any]:
        enhanced = partial_results.copy()
        enhanced["degradation_info"] = {
            "operation": operation,
            "failed_components": failed_components,
            "partial_success": True,
            "fallback_applied": True,
            "timestamp": datetime.now().isoformat(),
        }
        if operation == "network_discovery" and "open_ports" not in partial_results:
            enhanced["open_ports"] = self._basic_port_check(partial_results.get("target"))
        elif operation == "web_discovery" and "directories" not in partial_results:
            enhanced["directories"] = self._basic_directory_check(partial_results.get("target"))
        elif operation == "vulnerability_scanning" and "vulnerabilities" not in partial_results:
            enhanced["vulnerabilities"] = self._basic_security_check(partial_results.get("target"))

        enhanced["manual_recommendations"] = self._get_manual_recommendations(operation, failed_components)
        logger.info(f"🛡️ Graceful degradation applied for {operation}")
        return enhanced

    def _basic_port_check(self, target: str) -> List[int]:
        if not target:
            return []
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
        open_ports = []
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                if sock.connect_ex((target, port)) == 0:
                    open_ports.append(port)
                sock.close()
            except Exception:
                continue
        return open_ports

    def _basic_directory_check(self, target: str) -> List[str]:
        if not target:
            return []
        common_dirs = ["/admin", "/login", "/api", "/wp-admin", "/phpmyadmin", "/robots.txt"]
        found = []
        for d in common_dirs:
            try:
                url = f"{target.rstrip('/')}{d}"
                resp = requests.head(url, timeout=5, allow_redirects=True)
                if resp.status_code in [200, 301, 302, 403]:
                    found.append(d)
            except Exception:
                continue
        return found

    def _basic_security_check(self, target: str) -> List[Dict[str, Any]]:
        if not target:
            return []
        vulns = []
        try:
            resp = requests.get(target, timeout=10)
            security_headers = {
                "X-Frame-Options": "Clickjacking protection missing",
                "X-Content-Type-Options": "MIME type sniffing protection missing",
                "X-XSS-Protection": "XSS protection missing",
                "Strict-Transport-Security": "HTTPS enforcement missing",
                "Content-Security-Policy": "Content Security Policy missing",
            }
            for header, desc in security_headers.items():
                if header not in resp.headers:
                    vulns.append({"type": "missing_security_header", "severity": "medium",
                                  "description": desc, "header": header})
        except Exception as e:
            vulns.append({"type": "connection_error", "severity": "info",
                          "description": f"Could not check: {str(e)}"})
        return vulns

    def _get_manual_recommendations(self, operation: str, failed: List[str]) -> List[str]:
        base = {
            "network_discovery": ["Manually test common ports using telnet or nc"],
            "web_discovery": ["Manually browse common directories", "Check robots.txt"],
            "vulnerability_scanning": ["Manually test for common vulnerabilities"],
            "subdomain_enumeration": ["Use online subdomain discovery tools"],
        }
        recs = base.get(operation, [])
        for comp in failed:
            if comp == "nmap": recs.append("Consider using online port scanners")
            elif comp == "gobuster": recs.append("Try manual directory browsing")
            elif comp == "nuclei": recs.append("Perform manual vulnerability testing")
        return recs

    def is_critical_operation(self, operation: str) -> bool:
        return operation in self.critical_operations


# Global instance
degradation_manager = GracefulDegradation()