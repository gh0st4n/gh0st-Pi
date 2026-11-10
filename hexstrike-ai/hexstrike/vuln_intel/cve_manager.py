"""
HexStrike AI - CVE Intelligence Manager
"""
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CVEIntelligenceManager:
    """Advanced CVE Intelligence and Vulnerability Management System."""

    def __init__(self):
        self.cve_cache = {}
        self.vulnerability_db = {}

    def fetch_latest_cves(self, hours: int = 24, severity_filter: str = "HIGH,CRITICAL") -> Dict[str, Any]:
        try:
            logger.info(f"🔍 Fetching CVEs from last {hours} hours")
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=hours)
            start_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.000')
            end_str = end_date.strftime('%Y-%m-%dT%H:%M:%S.000')

            nvd_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            severity_levels = [s.strip().upper() for s in severity_filter.split(",")]
            all_cves = []

            params = {
                'lastModStartDate': start_str,
                'lastModEndDate': end_str,
                'resultsPerPage': 100,
            }

            try:
                response = requests.get(nvd_url, params=params, timeout=30)
                if response.status_code == 200:
                    nvd_data = response.json()
                    vulnerabilities = nvd_data.get('vulnerabilities', [])
                    logger.info(f"📊 Retrieved {len(vulnerabilities)} vulnerabilities from NVD")

                    for item in vulnerabilities:
                        cve_data = item.get('cve', {})
                        cve_id = cve_data.get('id', 'Unknown')
                        metrics = cve_data.get('metrics', {})
                        cvss_score = 0.0
                        severity = "UNKNOWN"

                        if 'cvssMetricV31' in metrics and metrics['cvssMetricV31']:
                            cvss_data = metrics['cvssMetricV31'][0]['cvssData']
                            cvss_score = cvss_data.get('baseScore', 0.0)
                            severity = cvss_data.get('baseSeverity', 'UNKNOWN').upper()
                        elif 'cvssMetricV2' in metrics and metrics['cvssMetricV2']:
                            cvss_data = metrics['cvssMetricV2'][0]['cvssData']
                            cvss_score = cvss_data.get('baseScore', 0.0)
                            if cvss_score >= 9.0: severity = "CRITICAL"
                            elif cvss_score >= 7.0: severity = "HIGH"
                            elif cvss_score >= 4.0: severity = "MEDIUM"
                            else: severity = "LOW"

                        if severity not in severity_levels and severity_levels != ['ALL']:
                            continue

                        descriptions = cve_data.get('descriptions', [])
                        description = "No description available"
                        for desc in descriptions:
                            if desc.get('lang') == 'en':
                                description = desc.get('value', description)
                                break

                        all_cves.append({
                            "cve_id": cve_id,
                            "description": description,
                            "severity": severity,
                            "cvss_score": cvss_score,
                            "published_date": cve_data.get('published', ''),
                            "last_modified": cve_data.get('lastModified', ''),
                            "source": "NVD",
                        })
                else:
                    logger.warning(f"⚠️ NVD API returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Error querying NVD API: {e}")

            return {
                "success": True,
                "cves": all_cves,
                "total_found": len(all_cves),
                "hours_searched": hours,
                "severity_filter": severity_filter,
                "data_sources": ["NVD API v2.0"],
            }
        except Exception as e:
            logger.error(f"💥 Error fetching CVEs: {e}")
            return {"success": False, "error": str(e), "cves": []}

    def analyze_cve_exploitability(self, cve_id: str) -> Dict[str, Any]:
        try:
            logger.info(f"🔬 Analyzing exploitability for {cve_id}")
            nvd_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            params = {'cveId': cve_id}

            response = requests.get(nvd_url, params=params, timeout=30)
            if response.status_code != 200:
                return {"success": False, "error": f"HTTP {response.status_code}", "cve_id": cve_id}

            nvd_data = response.json()
            vulnerabilities = nvd_data.get('vulnerabilities', [])
            if not vulnerabilities:
                return {"success": False, "error": f"CVE {cve_id} not found", "cve_id": cve_id}

            cve_data = vulnerabilities[0].get('cve', {})
            metrics = cve_data.get('metrics', {})
            cvss_score = 0.0
            severity = "UNKNOWN"
            attack_vector = "UNKNOWN"

            if 'cvssMetricV31' in metrics and metrics['cvssMetricV31']:
                cvss_data = metrics['cvssMetricV31'][0]['cvssData']
                cvss_score = cvss_data.get('baseScore', 0.0)
                severity = cvss_data.get('baseSeverity', 'UNKNOWN').upper()
                attack_vector = cvss_data.get('attackVector', 'UNKNOWN')

            exploit_score = 0.0
            if attack_vector == "NETWORK": exploit_score += 0.4
            elif attack_vector == "ADJACENT_NETWORK": exploit_score += 0.3
            elif attack_vector == "LOCAL": exploit_score += 0.2

            descriptions = cve_data.get('descriptions', [])
            description = ""
            for desc in descriptions:
                if desc.get('lang') == 'en':
                    description = desc.get('value', '')
                    break

            desc_lower = description.lower()
            if any(k in desc_lower for k in ['remote code execution', 'rce', 'buffer overflow']):
                exploit_score = min(exploit_score + 0.2, 1.0)
            elif any(k in desc_lower for k in ['authentication bypass', 'privilege escalation']):
                exploit_score = min(exploit_score + 0.15, 1.0)

            if exploit_score >= 0.8: level = "HIGH"
            elif exploit_score >= 0.6: level = "MEDIUM"
            elif exploit_score >= 0.3: level = "LOW"
            else: level = "VERY_LOW"

            return {
                "success": True,
                "cve_id": cve_id,
                "exploitability_score": round(exploit_score, 2),
                "exploitability_level": level,
                "cvss_score": cvss_score,
                "severity": severity,
                "attack_vector": attack_vector,
                "data_source": "NVD API v2.0",
                "analysis_timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"💥 Error analyzing CVE {cve_id}: {e}")
            return {"success": False, "error": str(e), "cve_id": cve_id}

    def search_existing_exploits(self, cve_id: str) -> Dict[str, Any]:
        try:
            logger.info(f"🔎 Searching exploits for {cve_id}")
            all_exploits = []

            try:
                github_url = "https://api.github.com/search/repositories"
                params = {'q': f'{cve_id} exploit poc', 'sort': 'updated', 'per_page': 5}
                resp = requests.get(github_url, params=params, timeout=15)
                if resp.status_code == 200:
                    for repo in resp.json().get('items', [])[:5]:
                        if cve_id.lower() in repo.get('name', '').lower() or \
                           cve_id.lower() in (repo.get('description') or '').lower():
                            all_exploits.append({
                                "source": "github",
                                "title": repo.get('name', ''),
                                "url": repo.get('html_url', ''),
                                "stars": repo.get('stargazers_count', 0),
                            })
            except Exception as e:
                logger.error(f"❌ GitHub search error: {e}")

            return {
                "success": True,
                "cve_id": cve_id,
                "exploits_found": len(all_exploits),
                "exploits": all_exploits,
                "search_timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"💥 Error searching exploits: {e}")
            return {"success": False, "error": str(e), "cve_id": cve_id, "exploits": []}


# Global instance
cve_intelligence = CVEIntelligenceManager()