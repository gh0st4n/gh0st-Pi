"""
HexStrike AI - CTF Tool Manager
"""
from typing import Dict, Any, List

from hexstrike.core.logging import setup_logging

logger = setup_logging()


class CTFToolManager:
    """Advanced tool manager for CTF challenges."""

    def __init__(self):
        self.tool_commands = {
            "httpx": "httpx -probe -tech-detect -status-code -title",
            "katana": "katana -depth 3 -js-crawl -form-extraction",
            "sqlmap": "sqlmap --batch --level 3 --risk 2 --threads 5",
            "dalfox": "dalfox url --mining-dom --mining-dict",
            "gobuster": "gobuster dir -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt,js",
            "dirsearch": "dirsearch -u {} -e php,html,js,txt -t 50",
            "feroxbuster": "feroxbuster -u {} -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
            "arjun": "arjun -u {} --get --post",
            "paramspider": "paramspider -d {}",
            "wpscan": "wpscan --url {} --enumerate ap,at,cb,dbe",
            "nikto": "nikto -h {} -C all",
            "hashcat": "hashcat -m 0 -a 0 --potfile-disable",
            "john": "john --wordlist=/usr/share/wordlists/rockyou.txt",
            "checksec": "checksec --file",
            "pwntools": "python3 -c 'from pwn import *'",
            "ropper": "ropper --file {} --search",
            "ropgadget": "ROPgadget --binary",
            "one-gadget": "one_gadget",
            "gdb-peda": "gdb -ex 'source /opt/peda/peda.py'",
            "angr": "python3 -c 'import angr'",
            "radare2": "r2 -A",
            "ghidra": "analyzeHeadless /tmp ghidra_project -import",
            "binwalk": "binwalk -e --dd='.*'",
            "foremost": "foremost -i {} -o /tmp/foremost_output",
            "exiftool": "exiftool -all",
            "steghide": "steghide extract -sf {} -p ''",
            "zsteg": "zsteg -a",
            "volatility": "volatility -f {} imageinfo",
            "volatility3": "python3 /opt/volatility3/vol.py -f",
            "wireshark": "tshark -r",
            "strings": "strings -n 8",
            "file": "file",
            "sherlock": "sherlock",
            "theHarvester": "theHarvester -d {} -b all",
            "subfinder": "subfinder -d",
            "amass": "amass enum -d",
            "whois": "whois",
            "dig": "dig",
            "shodan": "shodan search",
        }

        self.tool_categories = {
            "web_recon": ["httpx", "katana", "whatweb"],
            "web_vuln": ["sqlmap", "dalfox", "nikto", "wpscan"],
            "web_discovery": ["gobuster", "dirsearch", "feroxbuster"],
            "web_params": ["arjun", "paramspider"],
            "crypto_hash": ["hashcat", "john"],
            "pwn_analysis": ["checksec", "file", "strings"],
            "pwn_exploit": ["pwntools", "ropper", "ropgadget", "one-gadget"],
            "pwn_debug": ["gdb-peda", "angr"],
            "forensics_file": ["binwalk", "foremost", "exiftool"],
            "forensics_image": ["steghide", "zsteg"],
            "forensics_memory": ["volatility", "volatility3"],
            "forensics_network": ["wireshark"],
            "rev_static": ["ghidra", "radare2", "strings"],
            "osint_social": ["sherlock", "theHarvester"],
            "osint_domain": ["whois", "dig", "subfinder", "amass"],
        }

    def get_tool_command(self, tool: str, target: str, additional_args: str = "") -> str:
        base = self.tool_commands.get(tool, tool)
        if "{}" in base:
            base = base.format(target)
        else:
            base = f"{base} {target}"
        if additional_args:
            base += f" {additional_args}"
        return base

    def get_category_tools(self, category: str) -> List[str]:
        return self.tool_categories.get(category, [])

    def suggest_tools_for_challenge(self, description: str, category: str) -> List[str]:
        suggested = []
        desc = description.lower()

        if category == "web":
            suggested.extend(self.tool_categories["web_recon"][:2])
            if any(k in desc for k in ["sql", "injection", "database"]):
                suggested.append("sqlmap")
            if any(k in desc for k in ["xss", "script", "javascript"]):
                suggested.append("dalfox")
            if any(k in desc for k in ["wordpress", "wp"]):
                suggested.append("wpscan")
            if any(k in desc for k in ["directory", "hidden", "files"]):
                suggested.extend(["gobuster", "dirsearch"])
            if any(k in desc for k in ["parameter", "param"]):
                suggested.extend(["arjun", "paramspider"])
        elif category == "crypto":
            if any(k in desc for k in ["hash", "md5", "sha", "password"]):
                suggested.extend(["hashcat", "john"])
            if any(k in desc for k in ["rsa", "public key"]):
                suggested.extend(["ropper"])
        elif category == "pwn":
            suggested.extend(["checksec", "file", "strings"])
            if any(k in desc for k in ["buffer", "overflow", "bof"]):
                suggested.extend(["pwntools", "gdb-peda", "ropper"])
            if any(k in desc for k in ["rop", "gadget"]):
                suggested.extend(["ropper", "ropgadget"])
        elif category == "forensics":
            if any(k in desc for k in ["image", "jpg", "png", "steganography"]):
                suggested.extend(["exiftool", "steghide", "zsteg"])
            if any(k in desc for k in ["memory", "dump", "ram"]):
                suggested.extend(["volatility", "volatility3"])
            if any(k in desc for k in ["network", "pcap"]):
                suggested.append("wireshark")
            if any(k in desc for k in ["file", "deleted", "recovery"]):
                suggested.extend(["binwalk", "foremost"])
        elif category == "rev":
            suggested.extend(["file", "strings", "ghidra"])
            if any(k in desc for k in ["packed", "upx"]):
                suggested.append("checksec")
        elif category == "osint":
            if any(k in desc for k in ["username", "social"]):
                suggested.append("sherlock")
            if any(k in desc for k in ["domain", "subdomain", "dns"]):
                suggested.extend(["subfinder", "amass", "dig"])

        return list(dict.fromkeys(suggested))


# Global instance
ctf_tools = CTFToolManager()