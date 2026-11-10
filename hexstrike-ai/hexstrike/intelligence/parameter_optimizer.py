"""
HexStrike AI - Advanced Parameter Optimizer
"""
import os
import re
from datetime import datetime
from typing import Dict, Any, List

from hexstrike.intelligence.models import TargetProfile, TargetType, TechnologyStack
from hexstrike.intelligence.technology_detector import TechnologyDetector
from hexstrike.intelligence.rate_limiter import RateLimitDetector
from hexstrike.core.logging import setup_logging

logger = setup_logging()


class FailureRecoverySystem:
    """Intelligent failure recovery with alternative tool selection."""

    def __init__(self):
        self.tool_alternatives = {
            "nmap": ["rustscan", "masscan", "zmap"],
            "gobuster": ["dirsearch", "feroxbuster", "dirb"],
            "sqlmap": ["sqlninja", "bbqsql"],
            "nuclei": ["nikto", "w3af", "skipfish"],
            "hydra": ["medusa", "ncrack", "patator"],
            "hashcat": ["john", "ophcrack"],
            "amass": ["subfinder", "sublist3r", "assetfinder"],
            "ffuf": ["wfuzz", "gobuster", "dirb"],
        }
        self.failure_patterns = {
            "timeout": ["timeout", "timed out", "connection timeout"],
            "permission_denied": ["permission denied", "access denied", "forbidden"],
            "not_found": ["not found", "command not found", "no such file"],
            "network_error": ["network unreachable", "connection refused"],
            "rate_limited": ["rate limit", "too many requests", "throttled"],
        }

    def analyze_failure(self, error_output: str, exit_code: int) -> Dict[str, Any]:
        failure_type = "unknown"
        confidence = 0.0
        recovery_strategies = []
        error_lower = error_output.lower()

        for failure, patterns in self.failure_patterns.items():
            for pattern in patterns:
                if pattern in error_lower:
                    failure_type = failure
                    confidence += 0.3
                    break

        if exit_code == 124:
            failure_type = "timeout"; confidence += 0.5
        elif exit_code == 126:
            failure_type = "permission_denied"; confidence += 0.5

        confidence = min(1.0, confidence)

        strategy_map = {
            "timeout": ["Increase timeout values", "Reduce thread count", "Use alternative faster tool"],
            "permission_denied": ["Run with elevated privileges", "Check file permissions"],
            "rate_limited": ["Implement delays", "Reduce thread count", "Use stealth timing profile"],
            "network_error": ["Check network connectivity", "Try alternative routes"],
        }
        recovery_strategies = strategy_map.get(failure_type, ["Review error details"])

        return {
            "failure_type": failure_type,
            "confidence": confidence,
            "recovery_strategies": recovery_strategies,
            "alternative_tools": self.tool_alternatives.get(
                self._extract_tool_name(error_output), []
            ),
        }

    def _extract_tool_name(self, error_output: str) -> str:
        for tool in self.tool_alternatives:
            if tool in error_output.lower():
                return tool
        return "unknown"


class PerformanceMonitor:
    """Advanced performance monitoring with automatic resource allocation."""

    def __init__(self):
        self.resource_thresholds = {
            "cpu_high": 80.0, "memory_high": 85.0,
            "disk_high": 90.0, "network_high": 80.0,
        }

    def monitor_system_resources(self) -> Dict[str, float]:
        import psutil, time
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": mem.percent,
                "disk_percent": disk.percent,
                "network_bytes_sent": net.bytes_sent,
                "network_bytes_recv": net.bytes_recv,
                "timestamp": time.time(),
            }
        except Exception:
            return {}

    def optimize_based_on_resources(self, current_params: Dict[str, Any],
                                    resource_usage: Dict[str, float]) -> Dict[str, Any]:
        optimized = current_params.copy()
        optimizations = []

        if resource_usage.get("cpu_percent", 0) > self.resource_thresholds["cpu_high"]:
            if "threads" in optimized:
                orig = optimized["threads"]
                optimized["threads"] = max(1, int(orig * 0.5))
                optimizations.append(f"Reduced threads {orig}→{optimized['threads']}")

        if resource_usage.get("memory_percent", 0) > self.resource_thresholds["memory_high"]:
            if "batch_size" in optimized:
                orig = optimized["batch_size"]
                optimized["batch_size"] = max(1, int(orig * 0.6))
                optimizations.append(f"Reduced batch size {orig}→{optimized['batch_size']}")

        optimized["_optimizations_applied"] = optimizations
        return optimized


class ParameterOptimizer:
    """Advanced parameter optimization with intelligent context-aware selection."""

    def __init__(self):
        self.tech_detector = TechnologyDetector()
        self.rate_limiter = RateLimitDetector()
        self.failure_recovery = FailureRecoverySystem()
        self.performance_monitor = PerformanceMonitor()

        self.optimization_profiles = {
            "nmap": {
                "stealth": {"scan_type": "-sS", "timing": "-T2", "additional_args": "--max-retries 1"},
                "normal": {"scan_type": "-sS -sV", "timing": "-T4", "additional_args": "--max-retries 2"},
                "aggressive": {"scan_type": "-sS -sV -sC -O", "timing": "-T5", "additional_args": "--min-rate 1000"},
            },
            "gobuster": {
                "stealth": {"threads": 5, "delay": "1s", "timeout": "30s"},
                "normal": {"threads": 20, "delay": "0s", "timeout": "10s"},
                "aggressive": {"threads": 50, "delay": "0s", "timeout": "5s"},
            },
            "sqlmap": {
                "stealth": {"level": 1, "risk": 1, "threads": 1, "delay": 1},
                "normal": {"level": 2, "risk": 2, "threads": 5, "delay": 0},
                "aggressive": {"level": 3, "risk": 3, "threads": 10, "delay": 0},
            },
        }

    def optimize_parameters_advanced(self, tool: str, target_profile: TargetProfile,
                                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        if context is None:
            context = {}

        base_params = self._get_base_parameters(tool, target_profile)

        detected_tech = self.tech_detector.detect_technologies(
            target_profile.target,
            headers=context.get("headers", {}),
            content=context.get("content", ""),
            ports=target_profile.open_ports,
        )

        tech_params = self._apply_technology_optimizations(tool, base_params, detected_tech)

        resource_usage = self.performance_monitor.monitor_system_resources()
        resource_params = self.performance_monitor.optimize_based_on_resources(tech_params, resource_usage)

        profile = context.get("optimization_profile", "normal")
        final_params = self._apply_profile_optimizations(tool, resource_params, profile)

        final_params["_optimization_metadata"] = {
            "detected_technologies": detected_tech,
            "resource_usage": resource_usage,
            "optimization_profile": profile,
            "optimizations_applied": resource_params.get("_optimizations_applied", []),
            "timestamp": datetime.now().isoformat(),
        }
        return final_params

    def _get_base_parameters(self, tool: str, profile: TargetProfile) -> Dict[str, Any]:
        params = {"target": profile.target}
        if tool == "nmap":
            params.update({"scan_type": "-sS", "ports": "1-1000", "timing": "-T4"})
        elif tool == "gobuster":
            params.update({"mode": "dir", "threads": 20,
                           "wordlist": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"})
        elif tool == "sqlmap":
            params.update({"batch": True, "level": 1, "risk": 1})
        elif tool == "nuclei":
            params.update({"severity": "critical,high,medium", "threads": 25})
        return params

    def _apply_technology_optimizations(self, tool: str, params: Dict[str, Any],
                                        detected_tech: Dict[str, List[str]]) -> Dict[str, Any]:
        optimized = params.copy()
        if "wordpress" in detected_tech.get("cms", []):
            if tool == "gobuster":
                optimized["extensions"] = "php,html,txt,xml"
            elif tool == "nuclei":
                optimized["tags"] = optimized.get("tags", "") + ",wordpress"
        if "php" in detected_tech.get("languages", []):
            if tool == "gobuster":
                optimized["extensions"] = "php,php3,php4,php5,phtml,html"
            elif tool == "sqlmap":
                optimized["dbms"] = "mysql"
        if detected_tech.get("security", []):
            if any(w in detected_tech["security"] for w in ["cloudflare", "incapsula", "sucuri"]):
                optimized["_stealth_mode"] = True
                if tool == "gobuster":
                    optimized["threads"] = min(optimized.get("threads", 20), 5)
                    optimized["delay"] = "2s"
                elif tool == "sqlmap":
                    optimized["delay"] = 2
                    optimized["randomize"] = True
        return optimized

    def _apply_profile_optimizations(self, tool: str, params: Dict[str, Any],
                                     profile: str) -> Dict[str, Any]:
        if tool not in self.optimization_profiles:
            return params
        profile_settings = self.optimization_profiles[tool].get(profile, {})
        optimized = params.copy()
        for key, value in profile_settings.items():
            optimized[key] = value
        if params.get("_stealth_mode") and profile != "stealth":
            stealth = self.optimization_profiles[tool].get("stealth", {})
            for key, value in stealth.items():
                optimized[key] = value
        return optimized

    def handle_tool_failure(self, tool: str, error_output: str, exit_code: int,
                            current_params: Dict[str, Any]) -> Dict[str, Any]:
        analysis = self.failure_recovery.analyze_failure(error_output, exit_code)
        plan = {
            "original_tool": tool,
            "failure_analysis": analysis,
            "recovery_actions": [],
            "alternative_tools": analysis["alternative_tools"],
            "adjusted_parameters": current_params.copy(),
        }
        if analysis["failure_type"] == "timeout":
            if "timeout" in plan["adjusted_parameters"]:
                plan["adjusted_parameters"]["timeout"] *= 2
            if "threads" in plan["adjusted_parameters"]:
                plan["adjusted_parameters"]["threads"] = max(1, plan["adjusted_parameters"]["threads"] // 2)
            plan["recovery_actions"].append("Increased timeout and reduced threads")
        elif analysis["failure_type"] == "rate_limited":
            timing = self.rate_limiter.adjust_timing(plan["adjusted_parameters"], "stealth")
            plan["adjusted_parameters"].update(timing)
            plan["recovery_actions"].append("Applied stealth timing profile")
        return plan


# Global instance
parameter_optimizer = ParameterOptimizer()