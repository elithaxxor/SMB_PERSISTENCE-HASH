#!/bin/bash

# Dependencies: smbclient, enum4linux, nmap, smbmap
# Ensure required tools are installed
apt-get install smbclient enum4linux nmap smbmap -y

# Target IP or range
TARGET="192.168.1.0/24"

# Enumerate SMB shares and workgroups
echo "Enumerating SMB shares and workgroups..."
nmap -p 445 --script smb-enum-shares,smb-enum-users $TARGET > smb_enum_results.txt

# Using enum4linux for detailed enumeration
echo "Running enum4linux..."
enum4linux -a $TARGET >> smb_enum_results.txt

# Using smbclient to list shares
echo "Listing shares using smbclient..."
smbclient -L //$TARGET -N >> smb_enum_results.txt

# Using smbmap to enumerate shares
echo "Enumerating shares using smbmap..."
smbmap -H $TARGET >> smb_enum_results.txt

echo "SMB enumeration completed. Results saved in smb_enum_results.txt"

# Capture hashes without exporting
hashes=$(get_hashes_and_export)
echo "$hashes"

# Export hashes with flag
get_hashes_and_export --export-hashes
