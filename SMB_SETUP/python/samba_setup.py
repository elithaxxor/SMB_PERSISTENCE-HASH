#!/usr/bin/env python3
import os
import logging
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style, init

# Logging Configuration
LOG_DIR = "/var/log/samba_setup"
LOG_FILE = os.path.join(LOG_DIR, "samba_install.log")
MAX_LOG_SIZE = 5 * 1024 * 1024 * 1024  # 5GB

def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.chmod(LOG_DIR, 0o700)
    
    # Rotate logs if over 5GB
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        os.remove(LOG_FILE)
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=1
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s'
    ))
    logger.addHandler(file_handler)
    
    # Colored console handler
    class ColorFormatter(logging.Formatter):
        FORMATS = {
            logging.INFO: f"{Fore.GREEN}[+]{Style.RESET_ALL} %(message)s",
            logging.WARNING: f"{Fore.YELLOW}[!]{Style.RESET_ALL} %(message)s",
            logging.ERROR: f"{Fore.RED}[-]{Style.RESET_ALL} %(message)s"
        }
        
        def format(self, record):
            fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(fmt)
            return formatter.format(record)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)

# ... (rest of previous python implementation with logging integration)
