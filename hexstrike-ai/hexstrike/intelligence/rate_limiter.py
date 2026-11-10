"""
HexStrike AI - Rate Limit Detector
"""
import re
from typing import Dict, Any


class RateLimitDetector:
    """Intelligent rate limiting detection and automatic timing adjustment."""

    def __init__(self):
        self.rate_limit_indicators = [
            "rate limit", "too many requests", "429", "throttle",
            "slow down", "retry after", "quota exceeded", "api limit",
        ]
        self.timing_profiles = {
            "aggressive": {"delay": 0.1, "threads": 50, "timeout": 5},
            "normal": {"delay": 0.5, "threads": 20, "timeout": 10},
            "conservative": {"delay": 1.0, "threads": 10, "timeout": 15},
            "stealth": {"delay": 2.0, "threads": 5, "timeout": 30},
        }

    def detect_rate_limiting(self, response_text: str, status_code: int,
                             headers: Dict[str, str] = None) -> Dict[str, Any]:
        detected = False
        confidence = 0.0
        indicators = []

        if status_code == 429:
            detected = True; confidence += 0.8; indicators.append("HTTP 429")

        resp_lower = response_text.lower()
        for ind in self.rate_limit_indicators:
            if ind in resp_lower:
                detected = True; confidence += 0.2; indicators.append(f"Text: '{ind}'")

        if headers:
            for hname in headers:
                for rl in ["x-ratelimit", "retry-after", "x-rate-limit"]:
                    if rl in hname.lower():
                        detected = True; confidence += 0.3; indicators.append(f"Header: {hname}")

        confidence = min(1.0, confidence)
        return {
            "detected": detected,
            "confidence": confidence,
            "indicators": indicators,
            "recommended_profile": self._recommend_timing_profile(confidence),
        }

    def _recommend_timing_profile(self, confidence: float) -> str:
        if confidence >= 0.8: return "stealth"
        if confidence >= 0.5: return "conservative"
        if confidence >= 0.2: return "normal"
        return "aggressive"

    def adjust_timing(self, current_params: Dict[str, Any], profile: str) -> Dict[str, Any]:
        timing = self.timing_profiles.get(profile, self.timing_profiles["normal"])
        adjusted = current_params.copy()
        if "threads" in adjusted: adjusted["threads"] = timing["threads"]
        if "delay" in adjusted: adjusted["delay"] = timing["delay"]
        if "timeout" in adjusted: adjusted["timeout"] = timing["timeout"]
        if "additional_args" in adjusted:
            args = adjusted["additional_args"]
            args = re.sub(r'-t\s+\d+', '', args)
            args = re.sub(r'--threads\s+\d+', '', args)
            args += f" -t {timing['threads']}"
            if timing["delay"] > 0:
                args += f" --delay {timing['delay']}"
            adjusted["additional_args"] = args.strip()
        return adjusted


# Global instance
rate_limiter = RateLimitDetector()