import subprocess
import logging
from colorama import Fore, Style

def extract_smb_hashes():
    """Extract SMB hashes securely with root privileges"""
    try:
        logging.info(f"{Fore.YELLOW}[!]{Style.RESET_ALL} Starting hash extraction")
        result = subprocess.run(
            ["pdbedit", "-L", "-w"],
            check=True,
            capture_output=True,
            text=True
        )
        return parse_hashes(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"{Fore.RED}[-]{Style.RESET_ALL} Hash extraction failed: {e.stderr}")
        return []
    except Exception as e:
        logging.error(f"{Fore.RED}[-]{Style.RESET_ALL} Critical error: {str(e)}")
        return []

def parse_hashes(raw_output):
    """Parse and filter sensitive hash data"""
    valid_hashes = []
    for line in raw_output.splitlines():
        if ":" in line and not line.endswith(":$"):
            parts = line.split(":")
            if len(parts) >= 4:
                valid_hashes.append({
                    "username": parts[0],
                    "uid": parts[1],
                    "nt_hash": parts[3]
                })
    return valid_hashes

def display_hashes(hashes):
    """Format hashes for secure display"""
    print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Retrieved hashes:")
    for entry in hashes:
        print(f"{Fore.CYAN}User: {entry['username']}")
        print(f"  UID: {entry['uid']}")
        print(f"  NT Hash: {entry['nt_hash']}")
        print("-"*40)
