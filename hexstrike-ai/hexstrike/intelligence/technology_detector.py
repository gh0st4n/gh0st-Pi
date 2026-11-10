"""
HexStrike AI - Technology Detector
"""
from typing import Dict, List, Optional


class TechnologyDetector:
    """Advanced technology detection for context-aware parameter selection."""

    def __init__(self):
        self.detection_patterns = {
            "web_servers": {
                "apache": ["Apache", "apache", "httpd"],
                "nginx": ["nginx", "Nginx"],
                "iis": ["Microsoft-IIS", "IIS"],
                "tomcat": ["Tomcat", "Apache-Coyote"],
            },
            "frameworks": {
                "django": ["Django", "django", "csrftoken"],
                "flask": ["Flask", "Werkzeug"],
                "express": ["Express", "X-Powered-By: Express"],
                "laravel": ["Laravel", "laravel_session"],
                "rails": ["Ruby on Rails", "rails"],
                "spring": ["Spring", "JSESSIONID"],
            },
            "cms": {
                "wordpress": ["wp-content", "wp-includes", "WordPress", "/wp-admin/"],
                "drupal": ["Drupal", "drupal", "/sites/default/"],
                "joomla": ["Joomla", "joomla", "/administrator/"],
            },
            "databases": {
                "mysql": ["MySQL", "mysql", "phpMyAdmin"],
                "postgresql": ["PostgreSQL", "postgres"],
                "mssql": ["Microsoft SQL Server", "MSSQL"],
                "mongodb": ["MongoDB", "mongo"],
            },
            "languages": {
                "php": ["PHP", "php", ".php", "X-Powered-By: PHP"],
                "python": ["Python", "python", ".py"],
                "java": ["Java", "java", ".jsp"],
                "dotnet": ["ASP.NET", ".aspx", ".asp"],
                "nodejs": ["Node.js", "node"],
            },
            "security": {
                "waf": ["cloudflare", "CloudFlare", "X-CF-Ray", "incapsula", "sucuri"],
                "cdn": ["CloudFront", "Fastly", "KeyCDN", "Cloudflare"],
            },
        }
        self.port_services = {
            21: "ftp", 22: "ssh", 25: "smtp", 53: "dns", 80: "http",
            110: "pop3", 143: "imap", 443: "https", 1433: "mssql",
            3306: "mysql", 5432: "postgresql", 6379: "redis",
            8080: "http-alt", 8443: "https-alt", 27017: "mongodb",
        }

    def detect_technologies(self, target: str, headers: Dict[str, str] = None,
                            content: str = "", ports: List[int] = None) -> Dict[str, List[str]]:
        detected = {
            "web_servers": [], "frameworks": [], "cms": [],
            "databases": [], "languages": [], "security": [], "services": [],
        }
        if headers:
            for category, tech_patterns in self.detection_patterns.items():
                for tech, patterns in tech_patterns.items():
                    for hname, hval in headers.items():
                        for pattern in patterns:
                            if pattern.lower() in hval.lower() or pattern.lower() in hname.lower():
                                if tech not in detected[category]:
                                    detected[category].append(tech)
        if content:
            content_lower = content.lower()
            for category, tech_patterns in self.detection_patterns.items():
                for tech, patterns in tech_patterns.items():
                    for pattern in patterns:
                        if pattern.lower() in content_lower:
                            if tech not in detected[category]:
                                detected[category].append(tech)
        if ports:
            for port in ports:
                if port in self.port_services:
                    svc = self.port_services[port]
                    if svc not in detected["services"]:
                        detected["services"].append(svc)
        return detected


# Global instance
tech_detector = TechnologyDetector()