#!/usr/bin/env python3
import os
import re
import sys
import subprocess
import argparse
from getpass import getpass
from logging.handlers import RotatingFileHandler
import logging
from colorama import Fore, Style, init


# TODO:   create a websocket that willl persist as time goes by, so more hashes are picked up 

init(autoreset=True)
LOG_FILE = "/var/log/smb_manager.log"
MAX_LOG_SIZE = 5 * 1024 * 1024 * 1024  # 5GB

class SMBManager:
    def __init__(self):
        self.setup_logging()
        self.check_root()

    def setup_logging(self):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        logging.basicConfig(
            handlers=[RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=1)],
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.console = logging.StreamHandler()
        self.console.setFormatter(self.ColorFormatter())
        logging.getLogger().addHandler(self.console)

    class ColorFormatter(logging.Formatter):
        FORMATS = {
            logging.INFO: f"{Fore.GREEN}[+]{Style.RESET_ALL} %(message)s",
            logging.WARNING: f"{Fore.YELLOW}[!]{Style.RESET_ALL} %(message)s",
            logging.ERROR: f"{Fore.RED}[-]{Style.RESET_ALL} %(message)s"
        }

        def format(self, record):
            fmt = self.FORMATS.get(record.levelno, "%(message)s")
            return logging.Formatter(fmt).format(record)

    def check_root(self):
        if os.geteuid() != 0:
            logging.error("Requires root privileges")
            sys.exit(1)

    def install_samba(self):
        try:
            logging.info("Installing Samba...")
            subprocess.run(["apt-get", "update"], check=True)
            subprocess.run(["apt-get", "install", "-y", "samba"], check=True)
            subprocess.run(["cp", "/etc/samba/smb.conf", "/etc/samba/smb.conf.bak"], check=True)
            logging.info("Samba installed and configured")
        except subprocess.CalledProcessError as e:
            logging.error(f"Installation failed: {str(e)}")
            sys.exit(1)

    def configure_share(self):
        share_name = input(f"{Fore.YELLOW}[!]{Style.RESET_ALL} Enter share name: ")
        share_path = input(f"{Fore.YELLOW}[!]{Style.RESET_ALL} Enter share path: ")

        if not os.path.exists(share_path):
            create = input(f"{Fore.YELLOW}[!]{Style.RESET_ALL} Create path? (y/N): ").lower()
            if create == 'y':
                os.makedirs(share_path, exist_ok=True)
            else:
                logging.error("Share path not found")
                sys.exit(1)

        config = f"""
[{share_name}]
    path = {share_path}
    browseable = no
    writable = yes
    valid users = @smbusers
    create mask = 0660
    directory mask = 0770
        """
        with open("/etc/samba/smb.conf", "a") as f:
            f.write(config)
        logging.info("Share configuration written")

    def user_management(self):
        while True:
            username = input(f"{Fore.YELLOW}[!]{Style.RESET_ALL} Enter username (empty to finish): ")
            if not username: break
            
            try:
                subprocess.run(["useradd", "-M", "-s", "/usr/sbin/nologin", username], check=True)
                subprocess.run(["smbpasswd", "-a", "-s", username], input=f"{getpass()}n{getpass()}", text=True, check=True)
                logging.info(f"User {username} created")
            except subprocess.CalledProcessError:
                logging.error(f"Failed to create user {username}")

    def enumerate_smb(self):
        logging.info("Discovering workgroups...")
        result = subprocess.run(["nmblookup", "-S", "__SAMBA__"], capture_output=True, text=True)
        workgroups = re.findall(r'<GROUP>\s+(\S+)', result.stdout)
        
        logging.info("Enumerating users...")
        users = set()
        for wg in workgroups:
            result = subprocess.run(["rpcclient", "-U%", "-W", wg, "-c", "enumdomusers", "127.0.0.1"], 
                                  capture_output=True, text=True)
            users.update(re.findall(r'\[(.*?)\]', result.stdout))
        
        logging.info("Extracting hashes...")
        hashes = subprocess.check_output(["pdbedit", "-L", "-w"], text=True)
        
        print(f"{Fore.CYAN}=== SMB Audit Results ===")
        print(f"Workgroups: {', '.join(workgroups)}")
        print(f"Users: {', '.join(users)}")
        print(f"Hashes:n{hashes}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install and configure Samba")
    parser.add_argument("--audit", action="store_true", help="Enumerate SMB information")
    args = parser.parse_args()

    manager = SMBManager()
    
    if args.install:
        manager.install_samba()
        manager.configure_share()
        manager.user_management()
        subprocess.run(["systemctl", "restart", "smbd"])
    elif args.audit:
        manager.enumerate_smb()
    else:
        parser.print_help()
