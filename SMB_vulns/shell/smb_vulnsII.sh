#!/bin/bash

NETWORK="192.168.1.0/24"
SMB_HOSTS_LOG="smb_hosts.log"
SMB_VULN_LOG="smb_vulns.log"

# Tools check (simplified)
for tool in nmap smbclient rpcclient enum4linux crackmapexec smbmap; do
  command -v $tool >/dev/null 2>&1 || sudo apt-get install -y $tool
done

> "$SMB_HOSTS_LOG"
> "$SMB_VULN_LOG"

echo "[*] Scanning $NETWORK for SMB hosts..."
nmap -p139,445 --open -Pn -n -oG smb_hosts.gnmap "$NETWORK"
grep "139/open\|445/open" smb_hosts.gnmap | cut -d ' ' -f2 > "$SMB_HOSTS_LOG"

echo "[*] Checking SMB vulnerabilities on discovered hosts..."
nmap -p139,445 --script="smb-vuln-*" -iL "$SMB_HOSTS_LOG" -oN "$SMB_VULN_LOG"

nmap -p 139,445 --script smb-vuln* 192.168.1.100

# Further enumeration using discovered vulnerable hosts
while read -r ip; do
  echo "[*] Running smbclient and rpcclient enumeration on $ip"
  smbclient -L "//$ip/" -N
  rpcclient -U "" -N "$ip" -c "enumdomusers;enumdomgroups"
  enum4linux -a "$ip"
done < "$SMB_HOSTS_LOG"
