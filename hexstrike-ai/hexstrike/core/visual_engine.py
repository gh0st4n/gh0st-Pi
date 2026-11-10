"""
HexStrike AI - Modern Visual Engine
Beautiful, modern output formatting with animations and colors.
"""
from hexstrike.core.colors import HexStrikeColors as C


class ModernVisualEngine:
    """Beautiful, modern output formatting with animations and colors."""

    COLORS = {
        'MATRIX_GREEN': C.MATRIX_GREEN, 'NEON_BLUE': C.NEON_BLUE,
        'ELECTRIC_PURPLE': C.ELECTRIC_PURPLE, 'CYBER_ORANGE': C.CYBER_ORANGE,
        'HACKER_RED': C.HACKER_RED, 'TERMINAL_GRAY': C.TERMINAL_GRAY,
        'BRIGHT_WHITE': C.BRIGHT_WHITE, 'RESET': C.RESET,
        'BOLD': C.BOLD, 'DIM': C.DIM,
        'BLOOD_RED': C.BLOOD_RED, 'CRIMSON': C.CRIMSON,
        'DARK_RED': C.DARK_RED, 'FIRE_RED': C.FIRE_RED,
        'ROSE_RED': C.ROSE_RED, 'BURGUNDY': C.BURGUNDY,
        'SCARLET': C.SCARLET, 'RUBY': C.RUBY,
        'PRIMARY_BORDER': C.PRIMARY_BORDER, 'ACCENT_LINE': C.ACCENT_LINE,
        'ACCENT_GRADIENT': C.ACCENT_GRADIENT,
        'HIGHLIGHT_RED': C.HIGHLIGHT_RED, 'HIGHLIGHT_YELLOW': C.HIGHLIGHT_YELLOW,
        'HIGHLIGHT_GREEN': C.HIGHLIGHT_GREEN, 'HIGHLIGHT_BLUE': C.HIGHLIGHT_BLUE,
        'HIGHLIGHT_PURPLE': C.HIGHLIGHT_PURPLE,
        'SUCCESS': C.SUCCESS, 'WARNING': C.WARNING, 'ERROR': C.ERROR,
        'CRITICAL': C.CRITICAL, 'INFO': C.INFO, 'DEBUG': C.DEBUG,
        'VULN_CRITICAL': C.VULN_CRITICAL, 'VULN_HIGH': C.VULN_HIGH,
        'VULN_MEDIUM': C.VULN_MEDIUM, 'VULN_LOW': C.VULN_LOW,
        'VULN_INFO': C.VULN_INFO,
        'TOOL_RUNNING': C.TOOL_RUNNING, 'TOOL_SUCCESS': C.TOOL_SUCCESS,
        'TOOL_FAILED': C.TOOL_FAILED, 'TOOL_TIMEOUT': C.TOOL_TIMEOUT,
        'TOOL_RECOVERY': C.TOOL_RECOVERY,
        'PROGRESS_BAR': C.PROGRESS_BAR, 'PROGRESS_EMPTY': C.PROGRESS_EMPTY,
        'SPINNER': C.SPINNER, 'PULSE': C.PULSE,
    }

    PROGRESS_STYLES = {
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'bars': ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'],
        'arrows': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
        'pulse': ['●', '◐', '◑', '◒', '◓', '◔', '◕', '◖', '◗', '◘'],
    }

    @staticmethod
    def create_banner(api_host: str = "127.0.0.1", api_port: int = 8888) -> str:
        bc = ModernVisualEngine.COLORS['PRIMARY_BORDER']
        ac = ModernVisualEngine.COLORS['ACCENT_LINE']
        gr = ModernVisualEngine.COLORS['ACCENT_GRADIENT']
        R = ModernVisualEngine.COLORS['RESET']
        B = ModernVisualEngine.COLORS['BOLD']
        W = ModernVisualEngine.COLORS['BRIGHT_WHITE']
        G = ModernVisualEngine.COLORS['TERMINAL_GRAY']
        return f"""
{ac}{B}
██╗  ██╗███████╗██╗  ██╗███████╗████████╗██████╗ ██╗██╗  ██╗███████╗
██║  ██║██╔════╝╚██╗██╔╝██╔════╝╚══██╔══╝██╔══██╗██║██║ ██╔╝██╔════╝
███████║█████╗   ╚███╔╝ ███████╗   ██║   ██████╔╝██║█████╔╝ █████╗
██╔══██║██╔══╝   ██╔██╗ ╚════██║   ██║   ██╔══██╗██║██╔═██╗ ██╔══╝
██║  ██║███████╗██╔╝ ██╗███████║   ██║   ██║  ██║██║██║  ██╗███████╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝
{R}
{bc}┌─────────────────────────────────────────────────────────────────────┐
│  {W}🚀 HexStrike AI - Blood-Red Offensive Intelligence Core{bc}        │
│  {ac}⚡ AI-Automated Recon | Exploitation | Analysis Pipeline{bc}          │
│  {gr}🎯 Bug Bounty | CTF | Red Team | Zero-Day Research{bc}              │
└─────────────────────────────────────────────────────────────────────┘{R}
{G}[INFO] Server starting on {api_host}:{api_port}
[INFO] 150+ integrated modules | Adaptive AI decision engine active
[INFO] Blood-red theme engaged – unified offensive operations UI{R}
"""

    @staticmethod
    def render_progress_bar(progress: float, width: int = 40, style: str = 'cyber',
                            label: str = "", eta: float = 0, speed: str = "") -> str:
        progress = max(0.0, min(1.0, progress))
        filled_w = int(width * progress)
        empty_w = width - filled_w
        colors = ModernVisualEngine.COLORS
        if style == 'cyber':
            fc, ec = '█', '░'
            bar_c, prog_c = colors['ACCENT_LINE'], colors['PRIMARY_BORDER']
        elif style == 'matrix':
            fc, ec = '▓', '▒'
            bar_c, prog_c = colors['ACCENT_LINE'], colors['ACCENT_GRADIENT']
        elif style == 'neon':
            fc, ec = '━', '─'
            bar_c, prog_c = colors['PRIMARY_BORDER'], colors['CYBER_ORANGE']
        else:
            fc, ec = '█', '░'
            bar_c, prog_c = colors['ACCENT_LINE'], colors['PRIMARY_BORDER']
        filled = bar_c + fc * filled_w
        empty = colors['TERMINAL_GRAY'] + ec * empty_w
        pct = f"{progress * 100:.1f}%"
        extra = ""
        if eta > 0: extra += f" ETA: {eta:.1f}s"
        if speed: extra += f" Speed: {speed}"
        bar = f"[{filled}{empty}{colors['RESET']}] {prog_c}{pct}{colors['RESET']}"
        return f"{label}: {bar}{extra}" if label else f"{bar}{extra}"

    @staticmethod
    def create_progress_bar(current: int, total: int, width: int = 50, tool: str = "") -> str:
        pct = min(100, (current / total) * 100) if total else 0
        filled = int(width * pct / 100)
        bar = '█' * filled + '░' * (width - filled)
        bc = ModernVisualEngine.COLORS['PRIMARY_BORDER']
        fc = ModernVisualEngine.COLORS['ACCENT_LINE']
        R = ModernVisualEngine.COLORS['RESET']
        return f"""
{bc}┌─ {tool} ─{'─' * max(0, width - len(tool) - 4)}┐
│ {fc}{bar}{bc} │ {pct:6.1f}%
└─{'─' * (width + 10)}┘{R}"""

    @staticmethod
    def create_live_dashboard(processes: dict) -> str:
        colors = ModernVisualEngine.COLORS
        R = colors['RESET']
        if not processes:
            return f"""
{colors['PRIMARY_BORDER']}╭─────────────────────────────────────────────────────────────────────────────╮
│ {colors['ACCENT_LINE']}📊 HEXSTRIKE LIVE DASHBOARD{colors['PRIMARY_BORDER']}                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ {colors['TERMINAL_GRAY']}No active processes currently running{colors['PRIMARY_BORDER']}                                    │
╰─────────────────────────────────────────────────────────────────────────────╯{R}
"""
        lines = [
            f"{colors['PRIMARY_BORDER']}╭─────────────────────────────────────────────────────────────────────────────╮",
            f"│ {colors['ACCENT_LINE']}📊 HEXSTRIKE LIVE DASHBOARD{colors['PRIMARY_BORDER']}                                           │",
            f"├─────────────────────────────────────────────────────────────────────────────┤",
        ]
        for pid, info in processes.items():
            status = info.get('status', 'unknown')
            cmd = info.get('command', 'unknown')[:50]
            sc = colors['ACCENT_LINE'] if status == 'running' else colors['HACKER_RED']
            lines.append(f"│ {colors['CYBER_ORANGE']}PID {pid}{colors['PRIMARY_BORDER']} | {sc}{status}{colors['PRIMARY_BORDER']} | {colors['BRIGHT_WHITE']}{cmd}{colors['PRIMARY_BORDER']} │")
        lines.append(f"╰─────────────────────────────────────────────────────────────────────────────╯{R}")
        return "\n".join(lines)

    @staticmethod
    def format_vulnerability_card(vuln_data: dict) -> str:
        severity = vuln_data.get('severity', 'unknown').upper()
        name = vuln_data.get('name', 'Unknown Vulnerability')
        desc = vuln_data.get('description', 'No description available')
        colors = ModernVisualEngine.COLORS
        sev_colors = {
            'CRITICAL': colors['VULN_CRITICAL'], 'HIGH': colors['HACKER_RED'],
            'MEDIUM': colors['ACCENT_GRADIENT'], 'LOW': colors['CYBER_ORANGE'],
            'INFO': colors['TERMINAL_GRAY'],
        }
        color = sev_colors.get(severity, colors['TERMINAL_GRAY'])
        R = colors['RESET']
        W = colors['BRIGHT_WHITE']
        G = colors['TERMINAL_GRAY']
        return f"""
{color}┌─ 🚨 VULNERABILITY DETECTED ─────────────────────────────────────┐
│ {W}{name:<60}{color} │
│ {G}Severity: {color}{severity:<52}{color} │
│ {G}{desc[:58]:<58}{color} │
└─────────────────────────────────────────────────────────────────┘{R}"""

    @staticmethod
    def render_vulnerability_card(vuln_data: dict) -> str:
        return ModernVisualEngine.format_vulnerability_card(vuln_data)

    @staticmethod
    def format_error_card(error_type: str, tool_name: str, error_message: str,
                          recovery_action: str = "") -> str:
        colors = ModernVisualEngine.COLORS
        R = colors['RESET']
        ec = {
            'CRITICAL': colors['VULN_CRITICAL'], 'ERROR': colors['TOOL_FAILED'],
            'TIMEOUT': colors['TOOL_TIMEOUT'], 'RECOVERY': colors['TOOL_RECOVERY'],
            'WARNING': colors['WARNING'],
        }
        color = ec.get(error_type.upper(), colors['ERROR'])
        W = colors['BRIGHT_WHITE']
        card = f"""
{color}┌─ 🔥 ERROR DETECTED ─────────────────────────────────────────────┐{R}
{color}│ {W}Tool: {tool_name:<55}{color} │{R}
{color}│ {W}Type: {error_type:<55}{color} │{R}
{color}│ {W}Error: {error_message[:53]:<53}{color} │{R}"""
        if recovery_action:
            card += f"""
{color}│ {colors['TOOL_RECOVERY']}Recovery: {recovery_action[:50]:<50}{color} │{R}"""
        card += f"""
{color}└─────────────────────────────────────────────────────────────────┘{R}"""
        return card

    @staticmethod
    def format_tool_status(tool_name: str, status: str, target: str = "",
                           progress: float = 0.0) -> str:
        colors = ModernVisualEngine.COLORS
        R = colors['RESET']
        sc = {
            'RUNNING': colors['TOOL_RUNNING'], 'SUCCESS': colors['TOOL_SUCCESS'],
            'FAILED': colors['TOOL_FAILED'], 'TIMEOUT': colors['TOOL_TIMEOUT'],
            'RECOVERY': colors['TOOL_RECOVERY'], 'SKIPPED': colors['INFO'],
        }
        color = sc.get(status.upper(), colors['INFO'])
        pb = ""
        if progress > 0:
            filled = int(20 * progress)
            pb = f" [{colors['PROGRESS_BAR']}{'█' * filled}{colors['PROGRESS_EMPTY']}{'░' * (20 - filled)}{R}] {progress*100:.1f}%"
        return f"{color}🔧 {tool_name.upper()}{R} | {color}{status}{R} | {colors['BRIGHT_WHITE']}{target}{R}{pb}"

    @staticmethod
    def format_highlighted_text(text: str, highlight_type: str = "RED") -> str:
        colors = ModernVisualEngine.COLORS
        hc = {
            'RED': colors['HIGHLIGHT_RED'], 'YELLOW': colors['HIGHLIGHT_YELLOW'],
            'GREEN': colors['HIGHLIGHT_GREEN'], 'BLUE': colors['HIGHLIGHT_BLUE'],
            'PURPLE': colors['HIGHLIGHT_PURPLE'],
        }
        color = hc.get(highlight_type.upper(), colors['HIGHLIGHT_RED'])
        return f"{color} {text} {colors['RESET']}"

    @staticmethod
    def format_vulnerability_severity(severity: str, count: int = 0) -> str:
        colors = ModernVisualEngine.COLORS
        sc = {
            'CRITICAL': colors['VULN_CRITICAL'], 'HIGH': colors['VULN_HIGH'],
            'MEDIUM': colors['VULN_MEDIUM'], 'LOW': colors['VULN_LOW'],
            'INFO': colors['VULN_INFO'],
        }
        color = sc.get(severity.upper(), colors['INFO'])
        ct = f" ({count})" if count > 0 else ""
        return f"{color}{severity.upper()}{ct}{colors['RESET']}"

    @staticmethod
    def create_section_header(title: str, icon: str = "🔥", color: str = "FIRE_RED") -> str:
        colors = ModernVisualEngine.COLORS
        hc = colors.get(color, colors['FIRE_RED'])
        R = colors['RESET']
        return f"""
{hc}{'═' * 70}{R}
{hc}{icon} {title.upper()}{R}
{hc}{'═' * 70}{R}"""

    @staticmethod
    def format_command_execution(command: str, status: str, duration: float = 0.0) -> str:
        colors = ModernVisualEngine.COLORS
        R = colors['RESET']
        sc = {
            'STARTING': colors['INFO'], 'RUNNING': colors['TOOL_RUNNING'],
            'SUCCESS': colors['TOOL_SUCCESS'], 'FAILED': colors['TOOL_FAILED'],
            'TIMEOUT': colors['TOOL_TIMEOUT'],
        }
        color = sc.get(status.upper(), colors['INFO'])
        dt = f" ({duration:.2f}s)" if duration > 0 else ""
        cmd = command[:60] + ('...' if len(command) > 60 else '')
        return f"{color}▶ {cmd} | {status.upper()}{dt}{R}"

    @staticmethod
    def format_tool_output(tool: str, output: str, success: bool = True) -> str:
        colors = ModernVisualEngine.COLORS
        R = colors['RESET']
        B = colors['BOLD']
        status_icon = "✅" if success else "❌"
        status_color = colors['MATRIX_GREEN'] if success else colors['HACKER_RED']
        formatted = f"""
{B}╭─ 🛠️ {tool.upper()} OUTPUT ─────────────────────────────────────────────╮{R}
{B}│{R} {status_color}{status_icon} Status: {'SUCCESS' if success else 'FAILED'}{R}
{B}├─────────────────────────────────────────────────────────────────────────────┤{R}
"""
        lines = output.split('\n')
        for line in lines[:20]:
            if line.strip():
                ll = line.lower()
                if any(k in ll for k in ['error', 'failed', 'denied']):
                    formatted += f"{B}│{R} {colors['ERROR']}{line[:75]}{R}\n"
                elif any(k in ll for k in ['found', 'discovered', 'vulnerable']):
                    formatted += f"{B}│{R} {colors['MATRIX_GREEN']}{line[:75]}{R}\n"
                elif any(k in ll for k in ['warning', 'timeout']):
                    formatted += f"{B}│{R} {colors['WARNING']}{line[:75]}{R}\n"
                else:
                    formatted += f"{B}│{R} {colors['BRIGHT_WHITE']}{line[:75]}{R}\n"
        if len(lines) > 20:
            formatted += f"{B}│{R} {colors['TERMINAL_GRAY']}... ({len(lines) - 20} more lines truncated){R}\n"
        formatted += f"{B}╰─────────────────────────────────────────────────────────────────────────────╯{R}"
        return formatted

    @staticmethod
    def create_summary_report(results: dict) -> str:
        colors = ModernVisualEngine.COLORS
        R = colors['RESET']
        B = colors['BOLD']
        MG = colors['MATRIX_GREEN']
        vulns = results.get('vulnerabilities', [])
        total = len(vulns)
        critical = len([v for v in vulns if v.get('severity') == 'critical'])
        high = len([v for v in vulns if v.get('severity') == 'high'])
        exec_time = results.get('execution_time', 0)
        tools = results.get('tools_used', [])
        return f"""
{MG}{B}╔══════════════════════════════════════════════════════════════════════════════╗
║                              📊 SCAN SUMMARY REPORT                          ║
╠══════════════════════════════════════════════════════════════════════════════╣{R}
{B}║{R} {colors['NEON_BLUE']}🎯 Target:{R} {results.get('target', 'Unknown')[:60]}
{B}║{R} {colors['CYBER_ORANGE']}⏱️  Duration:{R} {exec_time:.2f} seconds
{B}║{R} {colors['WARNING']}🛠️  Tools Used:{R} {len(tools)} tools
{B}╠──────────────────────────────────────────────────────────────────────────────╣{R}
{B}║{R} {colors['HACKER_RED']}🔥 Critical:{R} {critical} vulnerabilities
{B}║{R} {colors['ERROR']}⚠️  High:{R} {high} vulnerabilities
{B}║{R} {MG}📈 Total Found:{R} {total} vulnerabilities
{B}╠──────────────────────────────────────────────────────────────────────────────╣{R}
{B}║{R} {colors['ELECTRIC_PURPLE']}🚀 Tools:{R} {', '.join(tools[:5])}{'...' if len(tools) > 5 else ''}
{MG}{B}╚══════════════════════════════════════════════════════════════════════════════╝{R}
"""