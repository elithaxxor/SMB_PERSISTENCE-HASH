#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root"
    exit 1
fi

# Update package lists
apt-get update

# Install Samba
apt-get install -y samba

# Backup original configuration
cp /etc/samba/smb.conf /etc/samba/smb.conf.bak

# Interactive configuration
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

# Create directory if needed
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

# User configuration
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

# Build configuration
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

# Set permissions
if [ "$GUESTOK" = "no" ] && [ ${#USERLIST[@]} -gt 0 ]; then
    chown -R ${USERLIST[0]}:"$SHAREPATH"
    chmod 2770 "$SHAREPATH"  # SGID to maintain group ownership
else
    chmod 2777 "$SHAREPATH"
    echo "Warning: Share is world-writable!" >&2
fi

# Enable and restart services
systemctl enable smbd
systemctl restart smbd

# Verify configuration
testparm -s

echo "Samba setup complete!"
echo "Share accessible at:"
echo "  Host: $(hostname -I | awk '{print $1}')"
echo "  Share: \\\\$(hostname | cut -d'.' -f1)\\$SHARENAME"
