"""
HexStrike AI - Intelligent Decision Engine
AI-powered tool selection dan parameter optimization.
"""
import re
import socket
import urllib.parse
from typing import Dict, Any, List, Optional

from hexstrike.intelligence.models import (
    TargetType, TechnologyStack, TargetProfile, AttackStep, AttackChain
)
from hexstrike.core.logging import setup_logging

logger = setup_logging()


class IntelligentDecisionEngine:
    """AI-powered tool selection dan parameter optimization."""

    def __init__(self):
        self.tool_effectiveness = self._initialize_tool_effectiveness()
        self.attack_patterns = self._initialize_attack_patterns()
        self._use_advanced_optimizer = True

    def _initialize_tool_effectiveness(self) -> Dict[str, Dict[str, float]]:
        return {
            TargetType.WEB_APPLICATION.value: {
                "nmap": 0.8, "gobuster": 0.9, "nuclei": 0.95,
                "nikto": 0.85, "sqlmap": 0.9, "ffuf": 0.9,
                "feroxbuster": 0.85, "katana": 0.88, "httpx": 0.85,
                "wpscan": 0.95, "dirsearch": 0.87, "gau": 0.82,
                "waybackurls": 0.8, "arjun": 0.9, "paramspider": 0.85,
                "x8": 0.88, "jaeles": 0.92, "dalfox": 0.93,
            },
            TargetType.NETWORK_HOST.value: {
                "nmap": 0.95, "nmap-advanced": 0.97, "masscan": 0.92,
                "rustscan": 0.9, "autorecon": 0.95, "enum4linux": 0.8,
                "enum4linux-ng": 0.88, "smbmap": 0.85, "rpcclient": 0.82,
                "nbtscan": 0.75, "arp-scan": 0.85, "responder": 0.88,
                "hydra": 0.8, "netexec": 0.85,
            },
            TargetType.API_ENDPOINT.value: {
                "nuclei": 0.9, "ffuf": 0.85, "arjun": 0.95,
                "paramspider": 0.88, "httpx": 0.9, "x8": 0.92,
                "katana": 0.85, "jaeles": 0.88,
            },
            TargetType.CLOUD_SERVICE.value: {
                "prowler": 0.95, "scout-suite": 0.92, "cloudmapper": 0.88,
                "pacu": 0.85, "trivy": 0.9, "clair": 0.85,
                "kube-hunter": 0.9, "kube-bench": 0.88,
                "docker-bench-security": 0.85, "falco": 0.87,
                "checkov": 0.9, "terrascan": 0.88,
            },
            TargetType.BINARY_FILE.value: {
                "ghidra": 0.95, "radare2": 0.9, "gdb": 0.85,
                "gdb-peda": 0.92, "angr": 0.88, "pwntools": 0.9,
                "ropgadget": 0.85, "ropper": 0.88, "one-gadget": 0.82,
                "checksec": 0.75, "strings": 0.7, "objdump": 0.75,
                "binwalk": 0.8, "pwninit": 0.85,
            },
        }

    def _initialize_attack_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "web_reconnaissance": [
                {"tool": "nmap", "priority": 1, "params": {"scan_type": "-sV -sC", "ports": "80,443,8080,8443"}},
                {"tool": "httpx", "priority": 2, "params": {"probe": True, "tech_detect": True}},
                {"tool": "katana", "priority": 3, "params": {"depth": 3, "js_crawl": True}},
                {"tool": "gau", "priority": 4, "params": {"include_subs": True}},
                {"tool": "nuclei", "priority": 5, "params": {"severity": "critical,high"}},
                {"tool": "dirsearch", "priority": 6, "params": {"extensions": "php,html,js,txt"}},
            ],
            "network_discovery": [
                {"tool": "arp-scan", "priority": 1, "params": {"local_network": True}},
                {"tool": "rustscan", "priority": 2, "params": {"ulimit": 5000, "scripts": True}},
                {"tool": "nmap-advanced", "priority": 3, "params": {"scan_type": "-sS", "os_detection": True}},
                {"tool": "masscan", "priority": 4, "params": {"rate": 1000, "ports": "1-65535"}},
                {"tool": "enum4linux-ng", "priority": 5, "params": {"shares": True, "users": True}},
            ],
            "vulnerability_assessment": [
                {"tool": "nuclei", "priority": 1, "params": {"severity": "critical,high,medium"}},
                {"tool": "jaeles", "priority": 2, "params": {"threads": 20}},
                {"tool": "dalfox", "priority": 3, "params": {"mining_dom": True}},
                {"tool": "nikto", "priority": 4, "params": {}},
                {"tool": "sqlmap", "priority": 5, "params": {"batch": True}},
            ],
            # ... pola lainnya (bug_bounty, binary, cloud, dll)
        }

    def analyze_target(self, target: str) -> TargetProfile:
        """Analisis target dan buat profil komprehensif."""
        profile = TargetProfile(target=target)
        profile.target_type = self._determine_target_type(target)

        if profile.target_type in [TargetType.WEB_APPLICATION, TargetType.API_ENDPOINT]:
            profile.ip_addresses = self._resolve_domain(target)

        if profile.target_type == TargetType.WEB_APPLICATION:
            profile.technologies = self._detect_technologies(target)
            profile.cms_type = self._detect_cms(target)

        profile.attack_surface_score = self._calculate_attack_surface(profile)
        profile.risk_level = self._determine_risk_level(profile)
        profile.confidence_score = self._calculate_confidence(profile)
        return profile

    def _determine_target_type(self, target: str) -> TargetType:
        if target.startswith(('http://', 'https://')):
            parsed = urllib.parse.urlparse(target)
            if '/api/' in parsed.path or parsed.path.endswith('/api'):
                return TargetType.API_ENDPOINT
            return TargetType.WEB_APPLICATION
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', target):
            return TargetType.NETWORK_HOST
        if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', target):
            return TargetType.WEB_APPLICATION
        if target.endswith(('.exe', '.bin', '.elf', '.so', '.dll')):
            return TargetType.BINARY_FILE
        return TargetType.UNKNOWN

    def _resolve_domain(self, target: str) -> List[str]:
        try:
            hostname = urllib.parse.urlparse(target).hostname if target.startswith('http') else target
            if hostname:
                return [socket.gethostbyname(hostname)]
        except Exception:
            pass
        return []

    def _detect_technologies(self, target: str) -> List[TechnologyStack]:
        technologies = []
        target_lower = target.lower()
        if 'wordpress' in target_lower or 'wp-' in target_lower:
            technologies.append(TechnologyStack.WORDPRESS)
        if 'php' in target_lower:
            technologies.append(TechnologyStack.PHP)
        if '.asp' in target_lower or '.aspx' in target_lower:
            technologies.append(TechnologyStack.DOTNET)
        return technologies or [TechnologyStack.UNKNOWN]

    def _detect_cms(self, target: str) -> Optional[str]:
        t = target.lower()
        if 'wordpress' in t or 'wp-' in t:
            return "WordPress"
        if 'drupal' in t:
            return "Drupal"
        if 'joomla' in t:
            return "Joomla"
        return None

    def _calculate_attack_surface(self, profile: TargetProfile) -> float:
        type_scores = {
            TargetType.WEB_APPLICATION: 7.0,
            TargetType.API_ENDPOINT: 6.0,
            TargetType.NETWORK_HOST: 8.0,
            TargetType.CLOUD_SERVICE: 5.0,
            TargetType.BINARY_FILE: 4.0,
        }
        score = type_scores.get(profile.target_type, 3.0)
        score += len(profile.technologies) * 0.5
        score += len(profile.open_ports) * 0.3
        if profile.cms_type:
            score += 1.5
        return min(score, 10.0)

    def _determine_risk_level(self, profile: TargetProfile) -> str:
        s = profile.attack_surface_score
        if s >= 8.0: return "critical"
        if s >= 6.0: return "high"
        if s >= 4.0: return "medium"
        if s >= 2.0: return "low"
        return "minimal"

    def _calculate_confidence(self, profile: TargetProfile) -> float:
        confidence = 0.5
        if profile.ip_addresses: confidence += 0.1
        if profile.technologies and profile.technologies[0] != TechnologyStack.UNKNOWN: confidence += 0.2
        if profile.cms_type: confidence += 0.1
        if profile.target_type != TargetType.UNKNOWN: confidence += 0.1
        return min(confidence, 1.0)

    def select_optimal_tools(self, profile: TargetProfile, objective: str = "comprehensive") -> List[str]:
        effectiveness = self.tool_effectiveness.get(profile.target_type.value, {})
        base_tools = list(effectiveness.keys())

        if objective == "quick":
            return sorted(base_tools, key=lambda t: effectiveness.get(t, 0), reverse=True)[:3]
        elif objective == "comprehensive":
            return [t for t in base_tools if effectiveness.get(t, 0) > 0.7]
        elif objective == "stealth":
            stealth = ["amass", "subfinder", "httpx", "nuclei"]
            return [t for t in base_tools if t in stealth]
        return base_tools

    def optimize_parameters(self, tool: str, profile: TargetProfile, context: Dict[str, Any] = None) -> Dict[str, Any]:
        if context is None:
            context = {}
        if self._use_advanced_optimizer:
            from hexstrike.intelligence.parameter_optimizer import parameter_optimizer
            return parameter_optimizer.optimize_parameters_advanced(tool, profile, context)
        return {"target": profile.target}

    def create_attack_chain(self, profile: TargetProfile, objective: str = "comprehensive") -> AttackChain:
        chain = AttackChain(profile)
        # Pilih pattern berdasarkan target type
        pattern_key = self._select_pattern_key(profile, objective)
        pattern = self.attack_patterns.get(pattern_key, [])

        for step_config in pattern:
            tool = step_config["tool"]
            params = self.optimize_parameters(tool, profile)
            effectiveness = self.tool_effectiveness.get(profile.target_type.value, {}).get(tool, 0.5)
            step = AttackStep(
                tool=tool,
                parameters=params,
                expected_outcome=f"Discover vulnerabilities using {tool}",
                success_probability=effectiveness * profile.confidence_score,
                execution_time_estimate=180,
            )
            chain.add_step(step)

        chain.calculate_success_probability()
        chain.risk_level = profile.risk_level
        return chain

    def _select_pattern_key(self, profile: TargetProfile, objective: str) -> str:
        mapping = {
            TargetType.WEB_APPLICATION: "web_reconnaissance",
            TargetType.NETWORK_HOST: "network_discovery",
            TargetType.API_ENDPOINT: "api_testing",
        }
        return mapping.get(profile.target_type, "web_reconnaissance")


# Global instance
decision_engine = IntelligentDecisionEngine()