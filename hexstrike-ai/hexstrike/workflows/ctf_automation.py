"""
HexStrike AI - CTF Challenge Automator
"""
import re
import time
from typing import Dict, Any, List

from hexstrike.workflows.ctf_manager import CTFChallenge, ctf_manager
from hexstrike.workflows.ctf_tools import ctf_tools
from hexstrike.core.logging import setup_logging

logger = setup_logging()


class CTFChallengeAutomator:
    """Advanced automation system for CTF challenge solving."""

    def __init__(self):
        self.active_challenges = {}
        self.solution_cache = {}

    def auto_solve_challenge(self, challenge: CTFChallenge) -> Dict[str, Any]:
        result = {
            "challenge_id": challenge.name,
            "status": "in_progress",
            "automated_steps": [],
            "manual_steps": [],
            "confidence": 0.0,
            "flag_candidates": [],
        }
        try:
            workflow = ctf_manager.create_ctf_challenge_workflow(challenge)
            for step in workflow.get("workflow_steps", []):
                step_result = {
                    "step": step.get("step"),
                    "action": step.get("action"),
                    "success": True,
                    "output": f"[AUTO] {step.get('description', '')}",
                    "tools_used": workflow.get("tools", [])[:3],
                }
                result["automated_steps"].append(step_result)
                result["confidence"] += 0.1

            if result["confidence"] < 0.5:
                result["manual_steps"] = self._generate_manual_guidance(challenge, result)
                result["status"] = "needs_manual_intervention"
            else:
                result["status"] = "analysis_complete"

            result["confidence"] = min(1.0, result["confidence"])
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        return result

    def _extract_flag_candidates(self, output: str) -> List[str]:
        patterns = [r'flag\{[^}]+\}', r'FLAG\{[^}]+\}', r'ctf\{[^}]+\}', r'CTF\{[^}]+\}']
        candidates = []
        for p in patterns:
            candidates.extend(re.findall(p, output, re.IGNORECASE))
        return list(set(candidates))

    def _generate_manual_guidance(self, challenge: CTFChallenge,
                                  current_result: Dict[str, Any]) -> List[Dict[str, str]]:
        guidance = []
        if challenge.category == "web":
            guidance = [
                {"action": "manual_source_review", "description": "Review all HTML/JS source"},
                {"action": "parameter_fuzzing", "description": "Fuzz parameters with custom payloads"},
            ]
        elif challenge.category == "crypto":
            guidance = [
                {"action": "cipher_research", "description": "Research the cipher type"},
                {"action": "frequency_analysis", "description": "Perform frequency analysis"},
            ]
        elif challenge.category == "pwn":
            guidance = [
                {"action": "manual_debugging", "description": "Debug the binary manually"},
                {"action": "exploit_development", "description": "Develop custom exploit"},
            ]
        elif challenge.category == "forensics":
            guidance = [
                {"action": "manual_analysis", "description": "Analyze file structures manually"},
                {"action": "steganography_deep_dive", "description": "Deep dive steganography"},
            ]
        elif challenge.category == "rev":
            guidance = [
                {"action": "algorithm_analysis", "description": "Focus on core algorithm"},
                {"action": "dynamic_analysis", "description": "Use dynamic analysis"},
            ]
        return guidance


# Global instance
ctf_automator = CTFChallengeAutomator()