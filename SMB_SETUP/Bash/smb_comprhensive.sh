#!/bin/bash

# Samba Installation and Configuration Script (Debian-based)

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# --- 0. Source .env file (if it exists) ---
if [ -f .env ]; then
  set -o allexport
  source .env
  set +o allexport
fi

# --- 1. Gathering Information ---

# 1.1. Workgroup Name
read -r -p "Enter the workgroup name (e.g., WORKGROUP): " WORKGROUP
WORKGROUP="${WORKGROUP:-WORKGROUP}"

# 1.2. NetBIOS Name (Server Name)
read -r -p "Enter the NetBIOS name (server name, e.g., MYSERVER): " NETBIOS_NAME
NETBIOS_NAME="${NETBIOS_NAME:-MYSERVER}"

# 1.3. Shared Directory Path
read -r -p "Enter the absolute path to the directory you want to share (e.g., /home/user/shared): " SHARED_DIR
if [ ! -d "$SHARED_DIR" ]; then
  echo -e "${RED}[-] Error: The specified shared directory '$SHARED_DIR' does not exist.${NC}"
  exit 1
fi
if [ ! -r "$SHARED_DIR" ] || [ ! -w "$SHARED_DIR" ] || [ ! -x "$SHARED_DIR" ]; then
  echo -e "${RED}[-] Error: The script does not have read, write, and execute permissions on '$SHARED_DIR'.${NC}"
  exit 1
fi

# 1.4. Share Name
read -r -p "Enter the name of the share (e.g., MyShare): " SHARE_NAME
SHARE_NAME="${SHARE_NAME:-MyShare}"

# 1.5. Share Comment (Optional)
read -r -p "Enter a short description for the share (optional, press Enter to skip): " SHARE_COMMENT

# 1.6. Guest Access - Modified for predetermined value
GUEST_ACCESS="yes"  # Set guest access to "yes" as per requirements
echo -e "${YELLOW}[!] Guest access will be enabled.${NC}"

# 1.7. User Access - Using pre-defined users from .env or defaults
ADMIN_USER="${ADMIN_USER:-enter user}"
ADMIN_PASS="${ADMIN_PASS:-enter pass}"
REGULAR_USER="${REGULAR_USER:-enter user}"
REGULAR_PASS="${REGULAR_PASS:-enter pass}"

#Confirm they do not exist, then create
for USER in "$ADMIN_USER" "$REGULAR_USER"; do
    if id "$USER" &>/dev/null; then
        echo -e "${YELLOW}[!] User '$USER' already exists.${NC}"
    else
         # Create the user (no home directory, no login shell)
        sudo useradd -M -s /sbin/nologin "$USER"
        if [ $? -ne 0 ]; then
            echo -e "${RED}[-] Error creating user '$USER'.  Check permissions.${NC}"
            exit 1
        fi
        echo -e "${GREEN}[+] User '$USER' created.${NC}"
    fi
done

#Set passwords
for USER in "$ADMIN_USER" "$REGULAR_USER"; do
   PASS=$(if [ "$USER" = "$ADMIN_USER" ]; then echo "$ADMIN_PASS"; else echo "$REGULAR_PASS"; fi)
    (echo "$PASS"; echo "$PASS") | sudo smbpasswd -a "$USER"
    if [ $? -ne 0 ]; then
        echo -e "${RED}[-] Error setting Samba password for '$USER'.${NC}"
        exit 1
     fi
   echo -e "${GREEN}[+] Samba password set for '$USER'.${NC}"
done



# 1.8.  Read-Only Access - Force to NO for base, control via specific settings
READ_ONLY="no" # We'll manage this at the user level
echo -e "${YELLOW}[!] Share will NOT be globally read-only. Permissions will be set per-user.${NC}"


# --- 2. Installation and Configuration ---

# 2.1. Update Package List
echo -e "${GREEN}[+] Updating package list...${NC}"
sudo apt-get update -y

# 2.2. Install Samba
echo -e "${GREEN}[+] Installing Samba...${NC}"
sudo apt-get install -y samba

# 2.3. Backup Original smb.conf
echo -e "${GREEN}[+] Backing up original smb.conf...${NC}"
sudo mv /etc/samba/smb.conf /etc/samba/smb.conf.bak

# 2.4. Create New smb.conf - Fine-grained permissions
echo -e "${GREEN}[+] Creating new smb.conf...${NC}"
sudo cat <<EOF > /etc/samba/smb.conf
[global]
   workgroup = $WORKGROUP
   netbios name = $NETBIOS_NAME
   server string = Samba Server %v
   security = user
   map to guest = Bad User
   dns proxy = no
   log file = /var/log/samba/log.%m
   max log size = 1000
   syslog = 0
   panic action = /usr/share/samba/panic-action %d

[$SHARE_NAME]
   comment = $SHARE_COMMENT
   path = $SHARED_DIR
   browseable = yes
   guest ok = yes
   read only = yes    #Default to read only for guests.
   write list = $ADMIN_USER
   valid users = $ADMIN_USER,$REGULAR_USER,@guest

   #Admin permissions
   admin users = $ADMIN_USER

EOF

# 2.5. Restart Samba Service
echo -e "${GREEN}[+] Restarting Samba service...${NC}"
sudo systemctl restart smbd.service nmbd.service

# 2.6. Check Samba status
echo -e "${GREEN}[+] Checking Samba service status:${NC}"
sudo systemctl status smbd.service nmbd.service

# 2.7 Enable Samba on boot.
sudo systemctl enable smbd.service nmbd.service

# --- 3. Firewall Configuration (ufw) ---
if command -v ufw &> /dev/null; then
    if sudo ufw status | grep -q "Status: active"; then
        echo -e "${GREEN}[+] Configuring UFW firewall...${NC}"
        sudo ufw allow samba
        echo -e "${GREEN}[+] UFW rules updated to allow Samba traffic.${NC}"
    else
        echo -e "${YELLOW}[!] UFW is installed but not active.  Consider enabling it: sudo ufw enable${NC}"
    fi
else
    echo -e "${YELLOW}[!] UFW firewall is not installed. Consider installing and configuring it for added security.${NC}"
fi


# --- 4.  Inform the user ---
echo -e "${GREEN}[+] Samba setup complete!${NC}"
echo "Share Name: $SHARE_NAME"
echo "Path: $SHARED_DIR"
echo "Workgroup: $WORKGROUP"
echo "NetBIOS Name: $NETBIOS_NAME"
echo "Guest Access: Enabled (Read-Only)"
echo "Admin User: $ADMIN_USER (Full Access)"
echo "Regular User: $REGULAR_USER (Read and Download)"


echo "You can access the share from other machines on your network."
echo "For Windows: \\\\$NETBIOS_NAME\\$SHARE_NAME or \\\\<server_ip_address>\\$SHARE_NAME"
echo "For Linux/macOS: smb://$NETBIOS_NAME/$SHARE_NAME or smb://<server_ip_address>/$SHARE_NAME"
echo "Use the appropriate credentials for admin or regular user access."

exit 0

