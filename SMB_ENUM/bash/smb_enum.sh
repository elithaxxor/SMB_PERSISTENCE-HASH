#!/bin/bash

# Check root privileges
if [[ $EUID -ne 0 ]]; then
    echo "[-] This script must be run as root for hash extraction"
    exit 1
fi

# Workgroup Discovery
echo "[+] Discovering workgroups..."
WORKGROUPS=$(nmblookup -S __SAMBA__ | grep -oP '<GROUP>\s+\K\S+' | sort -u)
echo "Found Workgroups:"
echo "$WORKGROUPS"

# User Enumeration
echo -e "\n[+] Enumerating users..."
for WG in $WORKGROUPS; do
    echo "=== Workgroup: $WG ==="
    rpcclient -U% -W "$WG" -c "enumdomusers" 127.0.0.1 2>/dev/null | \
        grep -oP '\[.*?\]' | tr -d '[]'
done | sort -u

# Hash Extraction
echo -e "\n[+] Extracting SMB hashes (requires root)..."
pdbedit -L -w | grep -v ':\$' | column -t -s:
