#!/usr/bin/env python3
"""Cek paritas refactor modular terhadap HexStrike upstream (versi satu-file).

Membandingkan:
  - endpoint server  : path + method (refactor: aplikasi Flask yang benar-benar dibangun lewat create_app())
  - tool MCP         : nama fungsi yang didekorasi @mcp.tool (dibaca lewat AST, tanpa import fastmcp)

Pemangkasan yang DISENGAJA dicatat di scripts/parity_ignore.txt (satu per baris, wajib beralasan):
    route /api/python/execute   # sengaja dihapus: eksekusi Python bebas tidak aman
    tool  execute_python_script # idem

Pemakaian (dari folder hexstrike-ai):
    python scripts/parity_check.py --upstream /path/ke/hexstrike-ai-upstream
    python scripts/parity_check.py --upstream ... --list              # tampilkan semua yang belum ada
    python scripts/parity_check.py --upstream ... --fail-on-missing   # exit 1 bila masih ada (utk CI / `make test`)

--upstream = folder yang berisi hexstrike_server.py dan hexstrike_mcp.py versi asli
(mis. `git clone https://github.com/0x4m4/hexstrike-ai.git /tmp/hexstrike-upstream`, commit d689933).
"""
import argparse
import ast
import collections
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _parse(path):
    with open(path, encoding="utf-8") as fh:
        return ast.parse(fh.read(), path)


def upstream_routes(path):
    out = {}
    for n in ast.walk(_parse(path)):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in n.decorator_list:
                if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == "route"
                        and d.args and isinstance(d.args[0], ast.Constant)):
                    methods = ["GET"]
                    for kw in d.keywords:
                        if kw.arg == "methods":
                            methods = sorted(ast.literal_eval(kw.value))
                    out[d.args[0].value] = tuple(methods)
    return out


def refactor_routes():
    sys.path.insert(0, ROOT)
    os.chdir(ROOT)
    import logging
    logging.disable(logging.CRITICAL)
    from hexstrike.api.app import create_app
    app = create_app(debug=False)
    out = {}
    for r in app.url_map.iter_rules():
        if r.endpoint == "static":
            continue
        out[r.rule] = tuple(sorted(m for m in r.methods if m not in ("HEAD", "OPTIONS")))
    return out


def tool_names(paths):
    out = set()
    for p in paths:
        for n in ast.walk(_parse(p)):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for d in n.decorator_list:
                    t = d.func if isinstance(d, ast.Call) else d
                    if isinstance(t, ast.Attribute) and t.attr == "tool":
                        out.add(n.name)
    return out


def refactor_mcp_files():
    files = [os.path.join(ROOT, "hexstrike_mcp.py")]
    for d, _, fs in os.walk(os.path.join(ROOT, "hexstrike", "mcp")):
        if "__pycache__" not in d:
            files += [os.path.join(d, f) for f in fs if f.endswith(".py")]
    return files


def read_ignore(path):
    ign = {"route": {}, "tool": {}}
    if not os.path.isfile(path):
        return ign
    for line in open(path, encoding="utf-8"):
        body, _, why = line.partition("#")
        parts = body.split()
        if len(parts) == 2 and parts[0] in ign:
            ign[parts[0]][parts[1]] = why.strip()
        elif body.strip():
            print(f"[peringatan] baris ignore tidak dikenali: {line.strip()}", file=sys.stderr)
    return ign


def show(title, items, listing):
    print(f"\n{title}: {len(items)}")
    if not items:
        return
    if listing:
        for i in sorted(items):
            print("   ", i)
    else:
        grp = collections.Counter("/".join(i.split("/")[:3]) if i.startswith("/") else i.split("_")[0] for i in items)
        print("    per kelompok:", ", ".join(f"{k} ({v})" for k, v in grp.most_common(10)))
        print("    (--list untuk daftar lengkap)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--upstream", required=True, help="folder upstream (berisi hexstrike_server.py & hexstrike_mcp.py)")
    ap.add_argument("--ignore", default=os.path.join(ROOT, "scripts", "parity_ignore.txt"))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--fail-on-missing", action="store_true")
    a = ap.parse_args()

    srv = os.path.join(a.upstream, "hexstrike_server.py")
    mcp = os.path.join(a.upstream, "hexstrike_mcp.py")
    for p in (srv, mcp):
        if not os.path.isfile(p):
            sys.exit(f"tidak ditemukan: {p}")

    ign = read_ignore(a.ignore)
    up_r, re_r = upstream_routes(srv), refactor_routes()
    up_t, re_t = tool_names([mcp]), tool_names(refactor_mcp_files())

    miss_r = {p for p in up_r if p not in re_r and p not in ign["route"]}
    diff_m = {f"{p}  upstream={'/'.join(up_r[p])} refactor={'/'.join(re_r[p])}" for p in up_r if p in re_r and up_r[p] != re_r[p]}
    extra_r = {p for p in re_r if p not in up_r}
    miss_t = {t for t in up_t if t not in re_t and t not in ign["tool"]}

    print(f"ENDPOINT : upstream={len(up_r)}  refactor={len(re_r)}  sama={len(set(up_r) & set(re_r))}  "
          f"sengaja-dibuang={sum(1 for p in up_r if p in ign['route'] and p not in re_r)}")
    print(f"TOOL MCP : upstream={len(up_t)}  refactor={len(re_t)}  sama={len(up_t & re_t)}  "
          f"sengaja-dibuang={sum(1 for t in up_t if t in ign['tool'] and t not in re_t)}")
    show("Endpoint BELUM ada di refactor", miss_r, a.list)
    show("Endpoint dengan METHOD berbeda", diff_m, True)
    show("Endpoint BARU di refactor (tidak ada di upstream)", extra_r, a.list)
    show("Tool MCP BELUM ada di refactor", miss_t, a.list)

    if a.fail_on_missing and (miss_r or miss_t or diff_m):
        sys.exit(1)


if __name__ == "__main__":
    main()
