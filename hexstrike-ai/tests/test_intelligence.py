"""
Intelligence module tests.
Run:
  uv run pytest tests/test_intelligence.py -v
"""
import pytest

pytestmark = pytest.mark.unit


class TestModels:
    def test_target_profile_defaults(self):
        from hexstrike.intelligence.models import TargetProfile, TargetType

        profile = TargetProfile(target="example.local")
        assert profile.target == "example.local"
        assert profile.target_type == TargetType.UNKNOWN
        assert profile.confidence_score == 0.0

    def test_target_profile_to_dict(self):
        from hexstrike.intelligence.models import TargetProfile, TargetType, TechnologyStack

        profile = TargetProfile(
            target="http://example.local",
            target_type=TargetType.WEB_APPLICATION,
            technologies=[TechnologyStack.PHP],
        )
        data = profile.to_dict()

        assert data["target"] == "http://example.local"
        assert data["target_type"] == "web_application"
        assert data["technologies"] == ["php"]

    def test_attack_chain_probability(self):
        from hexstrike.intelligence.models import TargetProfile, AttackChain, AttackStep

        chain = AttackChain(TargetProfile(target="example.local"))
        chain.add_step(
            AttackStep(
                tool="nmap",
                parameters={"target": "example.local"},
                expected_outcome="ports",
                success_probability=0.8,
                execution_time_estimate=10,
            )
        )
        chain.add_step(
            AttackStep(
                tool="nuclei",
                parameters={"target": "example.local"},
                expected_outcome="vulns",
                success_probability=0.5,
                execution_time_estimate=20,
            )
        )
        chain.calculate_success_probability()

        assert len(chain.steps) == 2
        assert chain.estimated_time == 30
        assert chain.success_probability == pytest.approx(0.4)
        assert "nmap" in chain.required_tools
        assert "nuclei" in chain.required_tools


class TestDecisionEngine:
    def test_analyze_web_target_without_network(self, monkeypatch):
        from hexstrike.intelligence.decision_engine import decision_engine
        from hexstrike.intelligence.models import TargetType

        monkeypatch.setattr(decision_engine, "_resolve_domain", lambda target: ["127.0.0.1"])

        profile = decision_engine.analyze_target("http://example.local")
        assert profile.target_type == TargetType.WEB_APPLICATION
        assert profile.ip_addresses == ["127.0.0.1"]
        assert profile.risk_level in {"medium", "high", "critical"}

    def test_analyze_api_target(self, monkeypatch):
        from hexstrike.intelligence.decision_engine import decision_engine
        from hexstrike.intelligence.models import TargetType

        monkeypatch.setattr(decision_engine, "_resolve_domain", lambda target: ["127.0.0.1"])

        profile = decision_engine.analyze_target("http://example.local/api/v1")
        assert profile.target_type == TargetType.API_ENDPOINT

    def test_analyze_ip_target(self):
        from hexstrike.intelligence.decision_engine import decision_engine
        from hexstrike.intelligence.models import TargetType

        profile = decision_engine.analyze_target("192.168.1.10")
        assert profile.target_type == TargetType.NETWORK_HOST

    def test_select_optimal_tools_quick(self, monkeypatch):
        from hexstrike.intelligence.decision_engine import decision_engine

        monkeypatch.setattr(decision_engine, "_resolve_domain", lambda target: ["127.0.0.1"])

        profile = decision_engine.analyze_target("http://example.local")
        tools = decision_engine.select_optimal_tools(profile, objective="quick")

        assert isinstance(tools, list)
        assert 1 <= len(tools) <= 3

    def test_create_attack_chain(self, monkeypatch):
        from hexstrike.intelligence.decision_engine import decision_engine

        monkeypatch.setattr(decision_engine, "_resolve_domain", lambda target: ["127.0.0.1"])
        monkeypatch.setattr(
            decision_engine,
            "optimize_parameters",
            lambda tool, profile, context=None: {"target": profile.target},
        )

        profile = decision_engine.analyze_target("http://example.local")
        chain = decision_engine.create_attack_chain(profile)

        assert len(chain.steps) > 0
        assert chain.estimated_time > 0
        assert 0 <= chain.success_probability <= 1


class TestTechnologyDetector:
    def test_detect_from_headers(self):
        from hexstrike.intelligence.technology_detector import TechnologyDetector

        detector = TechnologyDetector()
        result = detector.detect_technologies(
            "http://example.local",
            headers={"Server": "nginx", "X-Powered-By": "PHP/8.2"},
        )

        assert "nginx" in result["web_servers"]
        assert "php" in result["languages"]

    def test_detect_from_content(self):
        from hexstrike.intelligence.technology_detector import TechnologyDetector

        detector = TechnologyDetector()
        result = detector.detect_technologies(
            "http://example.local",
            content="<html><link href='/wp-content/themes/test.css'>WordPress</html>",
        )

        assert "wordpress" in result["cms"]

    def test_detect_from_ports(self):
        from hexstrike.intelligence.technology_detector import TechnologyDetector

        detector = TechnologyDetector()
        result = detector.detect_technologies(
            "example.local",
            ports=[22, 80, 443, 3306],
        )

        assert "ssh" in result["services"]
        assert "http" in result["services"]
        assert "mysql" in result["services"]


class TestRateLimiter:
    def test_rate_limit_detection_429(self):
        from hexstrike.intelligence.rate_limiter import RateLimitDetector

        detector = RateLimitDetector()
        result = detector.detect_rate_limiting(
            "Too Many Requests",
            429,
            {"Retry-After": "60"},
        )

        assert result["detected"] is True
        assert result["confidence"] >= 0.8
        assert result["recommended_profile"] in {"stealth", "conservative"}

    def test_adjust_timing(self):
        from hexstrike.intelligence.rate_limiter import RateLimitDetector

        detector = RateLimitDetector()
        adjusted = detector.adjust_timing(
            {"threads": 50, "delay": 0, "timeout": 5},
            "stealth",
        )

        assert adjusted["threads"] <= 5
        assert adjusted["delay"] >= 1
        assert adjusted["timeout"] >= 10


class TestParameterOptimizer:
    def test_parameter_optimizer_basic(self, monkeypatch):
        from hexstrike.intelligence.parameter_optimizer import ParameterOptimizer
        from hexstrike.intelligence.models import TargetProfile

        optimizer = ParameterOptimizer()

        monkeypatch.setattr(
            optimizer.performance_monitor,
            "monitor_system_resources",
            lambda: {
                "cpu_percent": 10.0,
                "memory_percent": 20.0,
                "disk_percent": 30.0,
            },
        )

        profile = TargetProfile(target="http://example.local")
        params = optimizer.optimize_parameters_advanced("nmap", profile)

        assert params["target"] == "http://example.local"
        assert "_optimization_metadata" in params
