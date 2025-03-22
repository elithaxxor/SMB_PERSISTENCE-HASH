#!/usr/bin/env python3
import subprocess
import sys
import re

def check_root():
    if os.geteuid() != 0:
        print("[-] Requires root privileges for hash extraction")
        sys.exit(1)

def get_workgroups():
    print("[+] Discovering workgroups...")
    result = subprocess.run(["nmblookup", "-S", "__SAMBA__"], capture_output=True, text=True)
    workgroups = re.findall(r'<GROUP>\s+(\S+)', result.stdout)
    return sorted(set(workgroups))

def enum_users(workgroups):
    print("\n[+] Enumerating users...")
    users = set()
    for wg in workgroups:
        cmd = f"rpcclient -U% -W '{wg}' -c 'enumdomusers' 127.0.0.1"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        matches = re.findall(r'\[(.*?)\]', result.stdout)
        users.update(matches)
    
    print("Found Users:")
    for user in sorted(users):
        print(f" - {user}")

def extract_hashes():
    print("\n[+] Extracting SMB hashes...")
    try:
        hashes = subprocess.check_output(
            ["pdbedit", "-L", "-w"], 
            stderr=subprocess.DEVNULL, 
            text=True
        )
        for line in hashes.splitlines():
            if ":" in line and not line.endswith(":$"):
                print(line)
    except Exception as e:
        print(f"[-] Hash extraction failed: {str(e)}")

if __name__ == "__main__":
    check_root()
    wgs = get_workgroups()
    print("Workgroups Found:\n" + "\n".join(wgs))
    enum_users(wgs)
    extract_hashes()
