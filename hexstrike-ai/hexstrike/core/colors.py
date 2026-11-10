"""
HexStrike AI - Color Definitions
Satu sumber warna untuk seluruh aplikasi.
"""

class HexStrikeColors:
    # Basic
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Extended palette
    MATRIX_GREEN = '\033[38;5;46m'
    NEON_BLUE = '\033[38;5;51m'
    ELECTRIC_PURPLE = '\033[38;5;129m'
    CYBER_ORANGE = '\033[38;5;208m'
    HACKER_RED = '\033[38;5;196m'
    TERMINAL_GRAY = '\033[38;5;240m'
    BRIGHT_WHITE = '\033[97m'

    # Reddish tones
    BLOOD_RED = '\033[38;5;124m'
    CRIMSON = '\033[38;5;160m'
    DARK_RED = '\033[38;5;88m'
    FIRE_RED = '\033[38;5;202m'
    ROSE_RED = '\033[38;5;167m'
    BURGUNDY = '\033[38;5;52m'
    SCARLET = '\033[38;5;197m'
    RUBY = '\033[38;5;161m'

    # Highlights
    HIGHLIGHT_RED = '\033[48;5;196m\033[38;5;15m'
    HIGHLIGHT_YELLOW = '\033[48;5;226m\033[38;5;16m'
    HIGHLIGHT_GREEN = '\033[48;5;46m\033[38;5;16m'
    HIGHLIGHT_BLUE = '\033[48;5;51m\033[38;5;16m'
    HIGHLIGHT_PURPLE = '\033[48;5;129m\033[38;5;15m'

    # Status
    SUCCESS = '\033[38;5;46m'
    WARNING = '\033[38;5;208m'
    ERROR = '\033[38;5;196m'
    CRITICAL = '\033[48;5;196m\033[38;5;15m\033[1m'
    INFO = '\033[38;5;51m'
    DEBUG = '\033[38;5;240m'

    # Vulnerability severity
    VULN_CRITICAL = '\033[48;5;124m\033[38;5;15m\033[1m'
    VULN_HIGH = '\033[38;5;196m\033[1m'
    VULN_MEDIUM = '\033[38;5;208m\033[1m'
    VULN_LOW = '\033[38;5;226m'
    VULN_INFO = '\033[38;5;51m'

    # Tool status
    TOOL_RUNNING = '\033[38;5;46m\033[5m'
    TOOL_SUCCESS = '\033[38;5;46m\033[1m'
    TOOL_FAILED = '\033[38;5;196m\033[1m'
    TOOL_TIMEOUT = '\033[38;5;208m\033[1m'
    TOOL_RECOVERY = '\033[38;5;129m\033[1m'

    # Progress
    PROGRESS_BAR = '\033[38;5;46m'
    PROGRESS_EMPTY = '\033[38;5;240m'
    SPINNER = '\033[38;5;51m'
    PULSE = '\033[38;5;196m\033[5m'

    # Unified theme
    PRIMARY_BORDER = CRIMSON
    ACCENT_LINE = HACKER_RED
    ACCENT_GRADIENT = BLOOD_RED


# Alias backward-compatible
Colors = HexStrikeColors