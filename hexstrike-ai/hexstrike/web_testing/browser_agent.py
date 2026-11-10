"""
HexStrike AI - Browser Agent
"""
import json
import time
import logging
from typing import Dict, Any, List

from hexstrike.core.visual_engine import ModernVisualEngine

logger = logging.getLogger(__name__)


class BrowserAgent:
    """AI-powered browser agent for web application testing."""

    def __init__(self):
        self.driver = None
        self.screenshots = []
        self.page_sources = []

    def setup_browser(self, headless: bool = True, proxy_port: int = None) -> bool:
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=HexStrike-BrowserAgent/1.0')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--ignore-certificate-errors')

            if proxy_port:
                chrome_options.add_argument(f'--proxy-server=http://127.0.0.1:{proxy_port}')

            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            logger.info("🌐 Browser Agent initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            return False

    def navigate_and_inspect(self, url: str, wait_time: int = 5) -> dict:
        try:
            if not self.driver:
                if not self.setup_browser():
                    return {'success': False, 'error': 'Failed to setup browser'}

            self.driver.get(url)
            time.sleep(wait_time)

            screenshot_path = f"/tmp/hexstrike_screenshot_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            self.screenshots.append(screenshot_path)

            from selenium.webdriver.common.by import By

            page_info = {
                'title': self.driver.title,
                'url': self.driver.current_url,
                'cookies': [{'name': c['name'], 'value': c['value'], 'domain': c['domain']}
                            for c in self.driver.get_cookies()],
                'forms': self._extract_forms(By),
                'links': self._extract_links(By),
                'scripts': self._extract_scripts(By),
            }

            security_analysis = self._analyze_page_security(self.driver.page_source, page_info)

            logger.info(f"🌐 Browser inspection completed: {url}")
            return {
                'success': True,
                'page_info': page_info,
                'security_analysis': security_analysis,
                'screenshot': screenshot_path,
            }
        except Exception as e:
            logger.error(f"❌ Browser inspection failed: {e}")
            return {'success': False, 'error': str(e)}

    def _extract_forms(self, By) -> list:
        forms = []
        try:
            for form in self.driver.find_elements(By.TAG_NAME, 'form'):
                form_data = {
                    'action': form.get_attribute('action') or '',
                    'method': form.get_attribute('method') or 'GET',
                    'inputs': [],
                }
                for inp in form.find_elements(By.TAG_NAME, 'input'):
                    form_data['inputs'].append({
                        'name': inp.get_attribute('name') or '',
                        'type': inp.get_attribute('type') or 'text',
                    })
                forms.append(form_data)
        except Exception:
            pass
        return forms

    def _extract_links(self, By) -> list:
        links = []
        try:
            for link in self.driver.find_elements(By.TAG_NAME, 'a')[:50]:
                href = link.get_attribute('href')
                if href:
                    links.append({'href': href, 'text': link.text[:100]})
        except Exception:
            pass
        return links

    def _extract_scripts(self, By) -> list:
        scripts = []
        try:
            for script in self.driver.find_elements(By.TAG_NAME, 'script')[:20]:
                src = script.get_attribute('src')
                if src:
                    scripts.append({'type': 'external', 'src': src})
                else:
                    content = script.get_attribute('innerHTML')
                    if content and len(content) > 10:
                        scripts.append({'type': 'inline', 'content': content[:1000]})
        except Exception:
            pass
        return scripts

    def _analyze_page_security(self, page_source: str, page_info: dict) -> dict:
        issues = []

        for storage_type, data in [('cookies', page_info.get('cookies', []))]:
            for item in data:
                name = item.get('name', '').lower()
                if any(s in name for s in ['password', 'token', 'secret', 'key']):
                    issues.append({
                        'type': 'sensitive_data_exposure',
                        'severity': 'high',
                        'description': f'Sensitive data in {storage_type}: {name}',
                    })

        for form in page_info.get('forms', []):
            has_csrf = any('csrf' in i.get('name', '').lower() or 'token' in i.get('name', '').lower()
                          for i in form.get('inputs', []))
            if not has_csrf and form.get('method', '').upper() == 'POST':
                issues.append({
                    'type': 'missing_csrf_protection',
                    'severity': 'medium',
                    'description': 'Form without CSRF protection',
                })

        return {
            'total_issues': len(issues),
            'issues': issues,
            'security_score': max(0, 100 - len(issues) * 10),
        }

    def run_active_tests(self, page_info: dict, payload: str = '<hexstrikeXSSTest123>') -> dict:
        findings = []
        tested = 0
        import requests as req
        for form in page_info.get('forms', []):
            if form.get('method', 'GET').upper() != 'GET':
                continue
            params = []
            for inp in form.get('inputs', [])[:3]:
                if inp.get('type', 'text') in ('text', 'search'):
                    params.append(f"{inp.get('name', 'param')}={payload}")
            if not params:
                continue
            action = form.get('action') or page_info.get('url', '')
            test_url = action + ('&' if '?' in action else '?') + '&'.join(params)
            try:
                r = req.get(test_url, timeout=8, verify=False)
                tested += 1
                if payload in r.text:
                    findings.append({
                        'type': 'reflected_xss', 'severity': 'high',
                        'description': 'Payload reflected', 'url': test_url,
                    })
            except Exception:
                continue
            if tested >= 5:
                break
        return {'active_findings': findings, 'tested_forms': tested}

    def close_browser(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("🌐 Browser closed")


# Global instance
browser_agent = BrowserAgent()