"""
HexStrike AI - HTTP Testing Framework (Burp Suite Alternative)
"""
import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

from hexstrike.core.visual_engine import ModernVisualEngine

logger = logging.getLogger(__name__)


class HTTPTestingFramework:
    """Advanced HTTP testing framework as Burp Suite alternative."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HexStrike-HTTP-Framework/1.0 (Advanced Security Testing)'
        })
        self.proxy_history = []
        self.vulnerabilities = []
        self.match_replace_rules = []
        self.scope = None
        self._req_id = 0

    def setup_proxy(self, proxy_port: int = 8080):
        self.session.proxies = {
            'http': f'http://127.0.0.1:{proxy_port}',
            'https': f'http://127.0.0.1:{proxy_port}',
        }

    def set_match_replace_rules(self, rules: list):
        self.match_replace_rules = rules or []

    def set_scope(self, host: str, include_subdomains: bool = True):
        self.scope = {'host': host, 'include_subdomains': include_subdomains}

    def _in_scope(self, url: str) -> bool:
        if not self.scope:
            return True
        try:
            h = urlparse(url).hostname or ''
            target = self.scope.get('host', '')
            if h == target:
                return True
            if self.scope.get('include_subdomains') and h.endswith('.' + target):
                return True
        except Exception:
            return True
        return False

    def intercept_request(self, url: str, method: str = 'GET', data: dict = None,
                          headers: dict = None, cookies: dict = None) -> dict:
        try:
            if headers:
                self.session.headers.update(headers)
            if cookies:
                self.session.cookies.update(cookies)

            if method.upper() == 'GET':
                response = self.session.get(url, params=data, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, data=data, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, data=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=30)
            else:
                response = self.session.request(method, url, data=data, timeout=30)

            self._req_id += 1
            request_data = {
                'id': self._req_id, 'url': url, 'method': method,
                'headers': dict(response.request.headers), 'data': data,
                'timestamp': datetime.now().isoformat(),
            }
            response_data = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text[:10000],
                'size': len(response.content),
                'time': response.elapsed.total_seconds(),
            }

            self.proxy_history.append({'request': request_data, 'response': response_data})
            self._analyze_response_for_vulns(url, response)

            return {
                'success': True,
                'request': request_data,
                'response': response_data,
                'vulnerabilities': self._get_recent_vulns(),
            }
        except Exception as e:
            logger.error(f"HTTP Framework error: {e}")
            return {'success': False, 'error': str(e)}

    def send_custom_request(self, request_spec: dict) -> dict:
        url = request_spec.get('url', '')
        method = request_spec.get('method', 'GET')
        headers = request_spec.get('headers') or {}
        cookies = request_spec.get('cookies') or {}
        data = request_spec.get('data')
        return self.intercept_request(url, method, data, headers, cookies)

    def spider_website(self, base_url: str, max_depth: int = 3, max_pages: int = 100) -> dict:
        try:
            discovered_urls = set()
            forms = []
            to_visit = [(base_url, 0)]
            visited = set()

            while to_visit and len(discovered_urls) < max_pages:
                current_url, depth = to_visit.pop(0)
                if current_url in visited or depth > max_depth:
                    continue
                visited.add(current_url)

                try:
                    response = self.session.get(current_url, timeout=10)
                    if response.status_code == 200:
                        discovered_urls.add(current_url)
                        soup = BeautifulSoup(response.text, 'html.parser')

                        for link in soup.find_all('a', href=True):
                            full_url = urljoin(current_url, link['href'])
                            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                                if full_url not in visited and depth < max_depth:
                                    to_visit.append((full_url, depth + 1))

                        for form in soup.find_all('form'):
                            form_data = {
                                'url': current_url,
                                'action': urljoin(current_url, form.get('action', '')),
                                'method': form.get('method', 'GET').upper(),
                                'inputs': [],
                            }
                            for inp in form.find_all(['input', 'textarea', 'select']):
                                form_data['inputs'].append({
                                    'name': inp.get('name', ''),
                                    'type': inp.get('type', 'text'),
                                    'value': inp.get('value', ''),
                                })
                            forms.append(form_data)
                except Exception:
                    continue

            return {
                'success': True,
                'discovered_urls': list(discovered_urls),
                'forms': forms,
                'total_pages': len(discovered_urls),
                'vulnerabilities': self._get_recent_vulns(),
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _analyze_response_for_vulns(self, url: str, response):
        vulns = []
        security_headers = {
            'X-Frame-Options': 'Clickjacking protection missing',
            'X-Content-Type-Options': 'MIME type sniffing protection missing',
            'X-XSS-Protection': 'XSS protection missing',
            'Strict-Transport-Security': 'HTTPS enforcement missing',
            'Content-Security-Policy': 'Content Security Policy missing',
        }
        for header, desc in security_headers.items():
            if header not in response.headers:
                vulns.append({
                    'type': 'missing_security_header', 'severity': 'medium',
                    'description': desc, 'url': url, 'header': header,
                })

        sensitive_patterns = [
            (r'password\s*[:=]\s*["\']?([^"\'\s]+)', 'Password disclosure'),
            (r'api[_-]?key\s*[:=]\s*["\']?([^"\'\s]+)', 'API key disclosure'),
            (r'secret\s*[:=]\s*["\']?([^"\'\s]+)', 'Secret disclosure'),
        ]
        for pattern, desc in sensitive_patterns:
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            if matches:
                vulns.append({
                    'type': 'information_disclosure', 'severity': 'high',
                    'description': desc, 'url': url, 'matches': matches[:5],
                })

        sql_errors = ['SQL syntax error', 'mysql_fetch_array', 'ORA-01756',
                      'Microsoft OLE DB Provider', 'PostgreSQL query failed']
        for err in sql_errors:
            if err.lower() in response.text.lower():
                vulns.append({
                    'type': 'sql_injection_indicator', 'severity': 'high',
                    'description': f'Potential SQL injection: {err}', 'url': url,
                })

        self.vulnerabilities.extend(vulns)

    def _get_recent_vulns(self, limit: int = 10):
        return self.vulnerabilities[-limit:] if self.vulnerabilities else []


# Global instance
http_framework = HTTPTestingFramework()