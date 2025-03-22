#!/bin/bash

# Colors and Symbols
GREEN='\033[0;32m[+]\033[0m'
YELLOW='\033[1;33m[!]\033[0m'
RED='\033[0;31m[-]\033[0m'
NC='\033[0m'

# Logging Configuration
LOG_DIR="/var/log/samba_setup"
LOG_FILE="$LOG_DIR/install_$(date +%Y%m%d%H%M%S).log"
MAX_LOG_SIZE=$((5 * 1024 * 1024 * 1024)) # 5GB

# Initialize logging
setup_logging() {
    mkdir -p "$LOG_DIR"
    chmod 700 "$LOG_DIR"
    
    # Rotate logs if over 5GB
    find "$LOG_DIR" -name "*.log" -size +5G -exec rm -f {} \; 2>/dev/null
    
    exec > >(tee -a "$LOG_FILE")
    exec 2>&1
}

log() {
    local level=$1
    local message=$2
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "$timestamp $level $message"
    echo "$timestamp $level $message" >> "$LOG_FILE"
}

# Enhanced Output Functions
show_header() {
    clear
    echo -e "${YELLOW}=============================================="
    echo -e " Samba Secure Installation Manager"
    echo -e "==============================================${NC}"
    echo -e "${GREEN} Persistent logging enabled: ${LOG_FILE}"
    echo -e " Log rotation: 5GB maximum${NC}"
    echo
}

# ... (rest of previous bash implementation with logging calls)

# Example usage in main flow:
show_header
log "$YELLOW" "Starting installation process..."
log "$GREEN" "Successfully updated package lists"
log "$RED" "Failed to create directory - insufficient permissions"
