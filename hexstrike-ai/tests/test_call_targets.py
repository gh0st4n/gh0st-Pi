"""
Regression: setiap error_handler.<x>(...) yang dipanggil di kode HARUS ada di IntelligentErrorHandler.
Refactor sebelumnya kehilangan auto_adjust_parameters / escalate_to_human / _get_system_resources,
sehingga jalur pemulihan error meledak dengan AttributeError saat dipakai.
"""
import re
import inspect
from pathlib import Path

from hexstrike.error_handling.handler import error_handler, IntelligentErrorHandler

PKG = Path(__file__).resolve().parents[1] / "hexstrike"


def _called_names():
    names = {}
    for path in PKG.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"\berror_handler\.([A-Za-z_][A-Za-z0-9_]*)\(", text):
            names.setdefault(m.group(1), set()).add(path.name)
    return names


def test_every_called_method_exists():
    missing = {n: sorted(f) for n, f in _called_names().items() if not hasattr(error_handler, n)}
    assert not missing, f"dipanggil tapi tidak ada di IntelligentErrorHandler: {missing}"


def test_get_alternative_tool_accepts_context():
    # recovery.py memanggil get_alternative_tool(tool, context)
    params = inspect.signature(IntelligentErrorHandler.get_alternative_tool).parameters
    assert "context" in params
