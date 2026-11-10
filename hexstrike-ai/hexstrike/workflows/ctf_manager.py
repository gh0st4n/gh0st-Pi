"""
HexStrike AI - CTF Workflow Manager
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List

from hexstrike.core.logging import setup_logging

logger = setup_logging()


@dataclass
class CTFChallenge:
    name: str
    category: str
    description: str
    points: int = 0
    difficulty: str = "unknown"
    files: List[str] = field(default_factory=list)
    url: str = ""
    hints: List[str] = field(default_factory=list)
    target: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name, "category": self.category,
            "description": self.description, "points": self.points,
            "difficulty": self.difficulty, "files": self.files,
            "url": self.url, "hints": self.hints, "target": self.target,
        }


class CTFWorkflowManager:
    """Specialized workflow manager for CTF competitions."""

    def __init__(self):
        self.solving_strategies = {
            "web": [
                {"strategy": "source_code_analysis", "description": "Analyze HTML/JS source"},
                {"strategy": "sql_injection", "description": "Test for SQL injection"},
                {"strategy": "xss_exploitation", "description": "Test for XSS"},
                {"strategy": "authentication_bypass", "description": "Test auth bypass"},
                {"strategy": "file_upload_bypass", "description": "Test file upload bypasses"},
            ],
            "crypto": [
                {"strategy": "frequency_analysis", "description": "Frequency analysis for substitution ciphers"},
                {"strategy": "known_plaintext", "description": "Known plaintext attacks"},
                {"strategy": "weak_keys", "description": "Test for weak cryptographic keys"},
                {"strategy": "mathematical_attacks", "description": "Mathematical property attacks"},
            ],
            "pwn": [
                {"strategy": "buffer_overflow", "description": "Exploit buffer overflows"},
                {"strategy": "format_string", "description": "Exploit format string vulns"},
                {"strategy": "rop_chains", "description": "Build ROP chains"},
                {"strategy": "heap_exploitation", "description": "Exploit heap vulnerabilities"},
            ],
            "forensics": [
                {"strategy": "file_carving", "description": "Recover deleted/hidden files"},
                {"strategy": "metadata_analysis", "description": "Analyze file metadata"},
                {"strategy": "steganography", "description": "Extract hidden data"},
                {"strategy": "memory_analysis", "description": "Analyze memory dumps"},
            ],
            "rev": [
                {"strategy": "static_analysis", "description": "Static binary analysis"},
                {"strategy": "dynamic_analysis", "description": "Dynamic binary analysis"},
                {"strategy": "algorithm_recovery", "description": "Reverse engineer algorithms"},
                {"strategy": "key_recovery", "description": "Extract encryption keys"},
            ],
        }

    def create_ctf_challenge_workflow(self, challenge: CTFChallenge) -> Dict[str, Any]:
        from hexstrike.workflows.ctf_tools import ctf_tools

        workflow = {
            "challenge": challenge.name,
            "category": challenge.category,
            "difficulty": challenge.difficulty,
            "points": challenge.points,
            "tools": ctf_tools.suggest_tools_for_challenge(challenge.description, challenge.category),
            "strategies": self.solving_strategies.get(challenge.category, []),
            "estimated_time": 0,
            "success_probability": 0.0,
            "workflow_steps": self._create_category_workflow(challenge),
        }

        base_times = {"easy": 1800, "medium": 3600, "hard": 7200, "insane": 14400, "unknown": 5400}
        category_mult = {"web": 1.0, "crypto": 1.3, "pwn": 1.5, "forensics": 1.2,
                         "rev": 1.4, "misc": 0.8, "osint": 0.9}
        base = base_times.get(challenge.difficulty, 5400)
        mult = category_mult.get(challenge.category, 1.0)
        workflow["estimated_time"] = int(base * mult)

        base_success = {"easy": 0.85, "medium": 0.65, "hard": 0.45, "insane": 0.25, "unknown": 0.55}
        tool_bonus = min(0.15, len(workflow["tools"]) * 0.02)
        workflow["success_probability"] = min(0.95, base_success.get(challenge.difficulty, 0.55) + tool_bonus)

        return workflow

    def _create_category_workflow(self, challenge: CTFChallenge) -> List[Dict[str, Any]]:
        workflows = {
            "web": [
                {"step": 1, "action": "reconnaissance", "description": "Analyze target URL"},
                {"step": 2, "action": "source_analysis", "description": "Examine source code"},
                {"step": 3, "action": "directory_discovery", "description": "Discover hidden dirs"},
                {"step": 4, "action": "vulnerability_testing", "description": "Test for vulns"},
                {"step": 5, "action": "exploitation", "description": "Exploit found vulns"},
                {"step": 6, "action": "flag_extraction", "description": "Extract flag"},
            ],
            "crypto": [
                {"step": 1, "action": "cipher_identification", "description": "Identify cipher type"},
                {"step": 2, "action": "key_analysis", "description": "Analyze key properties"},
                {"step": 3, "action": "attack_selection", "description": "Select attack method"},
                {"step": 4, "action": "implementation", "description": "Execute the attack"},
                {"step": 5, "action": "verification", "description": "Verify result"},
                {"step": 6, "action": "flag_extraction", "description": "Extract flag"},
            ],
            "pwn": [
                {"step": 1, "action": "binary_analysis", "description": "Analyze binary protections"},
                {"step": 2, "action": "vulnerability_discovery", "description": "Find vulnerabilities"},
                {"step": 3, "action": "exploit_development", "description": "Develop exploit"},
                {"step": 4, "action": "local_testing", "description": "Test locally"},
                {"step": 5, "action": "remote_exploitation", "description": "Exploit remote target"},
                {"step": 6, "action": "shell_interaction", "description": "Get flag from shell"},
            ],
            "forensics": [
                {"step": 1, "action": "file_analysis", "description": "Analyze files"},
                {"step": 2, "action": "data_recovery", "description": "Recover hidden data"},
                {"step": 3, "action": "artifact_extraction", "description": "Extract artifacts"},
                {"step": 4, "action": "timeline_reconstruction", "description": "Reconstruct timeline"},
                {"step": 5, "action": "correlation_analysis", "description": "Correlate findings"},
                {"step": 6, "action": "flag_discovery", "description": "Find flag"},
            ],
            "rev": [
                {"step": 1, "action": "static_analysis", "description": "Static analysis"},
                {"step": 2, "action": "dynamic_analysis", "description": "Dynamic analysis"},
                {"step": 3, "action": "algorithm_identification", "description": "Identify algorithms"},
                {"step": 4, "action": "key_extraction", "description": "Extract keys"},
                {"step": 5, "action": "solution_implementation", "description": "Implement solution"},
                {"step": 6, "action": "flag_generation", "description": "Generate flag"},
            ],
        }
        return workflows.get(challenge.category, [
            {"step": 1, "action": "analysis", "description": "Analyze the challenge"},
            {"step": 2, "action": "research", "description": "Research techniques"},
            {"step": 3, "action": "implementation", "description": "Implement solution"},
            {"step": 4, "action": "testing", "description": "Test solution"},
            {"step": 5, "action": "flag_submission", "description": "Submit flag"},
        ])


# Global instance
ctf_manager = CTFWorkflowManager()