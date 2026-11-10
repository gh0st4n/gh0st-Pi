"""
HexStrike AI - Flask Application Factory
"""
from flask import Flask


def create_app(debug: bool = False) -> Flask:
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False

    from hexstrike.api.health import bp as health_bp
    from hexstrike.api.command import bp as command_bp
    from hexstrike.api.files import bp as files_bp
    from hexstrike.api.tools_network import bp as tools_network_bp
    from hexstrike.api.tools_web import bp as tools_web_bp
    from hexstrike.api.tools_binary import bp as tools_binary_bp
    from hexstrike.api.tools_cloud import bp as tools_cloud_bp
    from hexstrike.api.tools_forensics import bp as tools_forensics_bp
    from hexstrike.api.intelligence import bp as intelligence_bp
    from hexstrike.api.bugbounty import bp as bugbounty_bp
    from hexstrike.api.ctf import bp as ctf_bp
    from hexstrike.api.vuln_intel import bp as vuln_intel_bp
    from hexstrike.api.process_mgmt import bp as process_bp
    from hexstrike.api.visual import bp as visual_bp
    from hexstrike.api.error_handling import bp as error_bp

    blueprints = [
        health_bp, command_bp, files_bp,
        tools_network_bp, tools_web_bp, tools_binary_bp,
        tools_cloud_bp, tools_forensics_bp,
        intelligence_bp, bugbounty_bp, ctf_bp,
        vuln_intel_bp, process_bp, visual_bp, error_bp,
    ]

    for bp in blueprints:
        app.register_blueprint(bp)

    return app