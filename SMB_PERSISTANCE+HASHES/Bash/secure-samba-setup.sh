#!/bin/bash

# Samba Secure Installation Script with Advanced Logging
# Version 2.0 - Unified Implementation


# Check root privileges
if [[ $EUID -ne 0 ]]; then
    echo "[-] This script must be run as root for hash extraction"
    exit 1
fi


# Configuration
LOG_DIR="/var/log/samba_install"
LOG_FILE="$LOG_DIR/install_$(date +%Y%m%d%H%M%S).log"
MAX_LOG_SIZE=5368709120  # 5GB in bytes
SAMBA_CONF="/etc/samba/smb.conf"

# Colors and Symbols
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'
PLUS="${GREEN}[+]${NC}"
MINUS="${RED}[-]${NC}"
INFO="${YELLOW}[!]${NC}"

# Initialization
init_logging() {
    mkdir -p "$LOG_DIR" && chmod 700 "$LOG_DIR"
    find "$LOG_DIR" -type f -size +${MAX_LOG_SIZE}c -exec rm -f {} \;
    exec > >(tee -a "$LOG_FILE") 2>&1
    echo -e "${PLUS} Logging initialized: ${LOG_FILE}"
}

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "${timestamp} $level ${message}" >> "$LOG_FILE"
}

show_header() {
    clear
    echo -e "${INFO}=============================================="
    echo -e " Samba Secure Installation Manager"
    echo -e "=============================================="
    echo -e "${PLUS} OS: $(lsb_release -ds)"
    echo -e "${PLUS} Kernel: $(uname -r)"
    echo -e "${PLUS} Logfile: ${LOG_FILE}\n${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${MINUS} This script must run as root"
        exit 1
    fi
}

install_samba() {
    echo -e "${INFO} Updating package repositories..."
    if apt-get update; then
        echo -e "${PLUS} Package lists updated"
    else
        echo -e "${MINUS} Failed to update packages"
        exit 1
    fi

    echo -e "${INFO} Installing Samba..."
    if apt-get install -y samba; then
        echo -e "${PLUS} Samba installed successfully"
    else
        echo -e "${MINUS} Samba installation failed"
        exit 1
    fi
}

configure_share() {
    echo -e "\n${INFO} Share Configuration"
    read -p "Enter share name: " SHARE_NAME
    read -p "Enter share path: " SHARE_PATH

    if [[ ! -d "$SHARE_PATH" ]]; then
        read -p "Path doesn't exist. Create? (Y/n) " CREATE
        if [[ $CREATE =~ ^[Yy]$ ]]; then
            mkdir -p "$SHARE_PATH" || {
                echo -e "${MINUS} Failed to create directory";
                exit 1;
            }
            echo -e "${PLUS} Created share directory: ${SHARE_PATH}"
        else
            echo -e "${MINUS} Aborting - directory not found"
            exit 1
        fi
    fi

    read -p "Make share writable? (Y/n) " WRITABLE
    read -p "Allow guest access? (y/N) " GUEST_ACCESS

    # Set defaults
    WRITABLE=${WRITABLE:-Y}
    GUEST_ACCESS=${GUEST_ACCESS:-N}

    # Configure share
    echo -e "\n${INFO} Configuring Samba share..."
    cp "$SAMBA_CONF" "${SAMBA_CONF}.bak"
    cat >> "$SAMBA_CONF" << EOF

[$SHARE_NAME]
    path = $SHARE_PATH
    browseable = yes
    writable = ${WRITABLE^^}
    guest ok = ${GUEST_ACCESS^^}
    create mask = 0770
    directory mask = 0770
EOF

    echo -e "${PLUS} Share configuration written"
}

user_management() {
    echo -e "\n${INFO} User Configuration"
    read -p "Create Samba users? (Y/n) " CREATE_USERS
    
    while [[ $CREATE_USERS =~ ^[Yy]$ ]]; do
        read -p "Enter username: " USERNAME
        
        # System user creation
        if ! id "$USERNAME" &>/dev/null; then
            useradd -m -s /usr/sbin/nologin "$USERNAME" && \
            passwd -l "$USERNAME" && \
            echo -e "${PLUS} System account created: ${USERNAME}"
        fi

        # Samba password setup
        if smbpasswd -L -a "$USERNAME"; then
            smbpasswd -L -e "$USERNAME"
            echo -e "${PLUS} Samba user activated: ${USERNAME}"
        else
            echo -e "${MINUS} Failed to create Samba user"
        fi

        read -p "Create another user? (y/N) " CREATE_USERS
        CREATE_USERS=${CREATE_USERS:-N}
    done
}

set_permissions() {
    echo -e "\n${INFO} Configuring permissions..."
    chmod 2770 "$SHARE_PATH"
    chown -R :sambashare "$SHARE_PATH"
    echo -e "${PLUS} Directory permissions set"
}

finalize() {
    systemctl restart smbd nmbd
    systemctl enable smbd nmbd
    testparm -s
    
    echo -e "\n${PLUS} Installation complete!"
    echo -e "${INFO} Access your share at:"
    echo -e " Windows: \\\\$(hostname -I | awk '{print $1}')\\${SHARE_NAME}"
    echo -e " Linux: smb://$(hostname -I | awk '{print $1}')/${SHARE_NAME}"
}

# Main Execution
show_header
check_root
init_logging
install_samba
configure_share
user_management
set_permissions
finalize

exit 0
