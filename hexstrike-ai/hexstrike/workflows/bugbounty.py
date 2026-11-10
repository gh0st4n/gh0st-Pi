"""
HexStrike AI - Bug Bounty Workflow Manager
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class BugBountyTarget:
    domain: str
    scope: List[str] = field(default_factory=list)
    out_of_scope: List[str] = field(default_factory=list)
    program_type: str = "web"
    priority_vulns: List[str] = field(default_factory=lambda: ["rce", "sqli", "xss", "idor", "ssrf"])
    bounty_range: str = "unknown"


class BugBountyWorkflowManager:
    """Specialized workflow untuk bug bounty hunting."""

    def __init__(self):
        self.high_impact_vulns = {
            "rce": {"priority": 10, "tools": ["nuclei", "jaeles", "sqlmap"]},
            "sqli": {"priority": 9, "tools": ["sqlmap", "nuclei"]},
            "ssrf": {"priority": 8, "tools": ["nuclei", "ffuf"]},
            "idor": {"priority": 8, "tools": ["arjun", "paramspider", "ffuf"]},
            "xss": {"priority": 7, "tools": ["dalfox", "nuclei"]},
            "lfi": {"priority": 7, "tools": ["ffuf", "nuclei"]},
        }

    def create_reconnaissance_workflow(self, target: BugBountyTarget) -> Dict[str, Any]:
        """Buat workflow recon komprehensif."""
        workflow = {"target": target.domain, "phases": [], "estimated_time": 0, "tools_count": 0}

        phases = [
            {
                "name": "subdomain_discovery",
                "tools": [
                    {"tool": "amass", "params": {"domain": target.domain}},
                    {"tool": "subfinder", "params": {"domain": target.domain}},
                ],
                "estimated_time": 300,
            },
            {
                "name": "http_service_discovery",
                "tools": [
                    {"tool": "httpx", "params": {"probe": True, "tech_detect": True}},
                ],
                "estimated_time": 180,
            },
            {
                "name": "content_discovery",
                "tools": [
                    {"tool": "katana", "params": {"depth": 3, "js_crawl": True}},
                    {"tool": "gau", "params": {"include_subs": True}},
                    {"tool": "dirsearch", "params": {"extensions": "php,html,js"}},
                ],
                "estimated_time": 600,
            },
            {
                "name": "parameter_discovery",
                "tools": [
                    {"tool": "paramspider", "params": {"level": 2}},
                    {"tool": "arjun", "params": {"method": "GET,POST"}},
                ],
                "estimated_time": 240,
            },
        ]

        workflow["phases"] = phases
        workflow["estimated_time"] = sum(p["estimated_time"] for p in phases)
        workflow["tools_count"] = sum(len(p["tools"]) for p in phases)
        return workflow

    def create_vulnerability_hunting_workflow(self, target: BugBountyTarget) -> Dict[str, Any]:
        """Buat workflow vulnerability hunting."""
        workflow = {"target": target.domain, "vulnerability_tests": [], "estimated_time": 0, "priority_score": 0}

        sorted_vulns = sorted(
            target.priority_vulns,
            key=lambda v: self.high_impact_vulns.get(v, {}).get("priority", 0),
            reverse=True,
        )

        for vuln_type in sorted_vulns:
            if vuln_type in self.high_impact_vulns:
                config = self.high_impact_vulns[vuln_type]
                test = {
                    "vulnerability_type": vuln_type,
                    "priority": config["priority"],
                    "tools": config["tools"],
                    "estimated_time": config["priority"] * 30,
                }
                workflow["vulnerability_tests"].append(test)
                workflow["estimated_time"] += test["estimated_time"]
                workflow["priority_score"] += config["priority"]

        return workflow


# Global instance
bugbounty_manager = BugBountyWorkflowManager()