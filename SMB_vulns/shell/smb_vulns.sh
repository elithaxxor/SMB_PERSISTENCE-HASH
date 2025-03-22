
NETWORK="192.168.1.0/24"
SMB_VULN_LOG="smb_vulns.log"

# Ensure required tools are installed
tools=(nmap smbclient rpcclient enum4linux crackmapexec smbmap)
for tool in "${tools[@]}"; do
  if ! command -v "$tool" &>/dev/null; then
    echo "[+] Installing missing tool: $tool"
    sudo apt-get update -y && sudo apt-get install -y "$tool"
  fi
done

# Start fresh log
> "$SMB_VULN_LOG"

echo "[*] Performing Nmap SMB vulnerability scan on network $NETWORK..."

# Run Nmap with SMB vulnerability scripts
nmap -p139,445 --script="smb-vuln-*" --open -Pn -n -oN "$SMB_VULN_LOG" "$NETWORK"

echo "[+] SMB vulnerability scanning complete. Results saved in $SMB_VULN_LOG"
