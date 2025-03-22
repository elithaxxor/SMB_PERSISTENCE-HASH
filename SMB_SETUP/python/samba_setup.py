#!/usr/bin/env python3
import os
import subprocess
import sys
from getpass import getpass

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, check=True)

def main():
    if os.geteuid() != 0:
        print("Please run as root")
        sys.exit(1)

    try:
        # Install dependencies
        run_cmd("apt-get update")
        run_cmd("apt-get install -y samba")
        
        # Backup config
        run_cmd("cp /etc/samba/smb.conf /etc/samba/smb.conf.bak")
        
        # Get user input
        share_name = input("Enter share name: ").strip()
        share_path = input("Enter full path to share directory: ").strip()
        browseable = input("Make share browseable? (yes/no) [no]: ").strip().lower() or "no"
        writable = input("Make share writable? (yes/no) [no]: ").strip().lower() or "no"
        guest_ok = input("Allow guest access? (yes/no) [no]: ").strip().lower() or "no"
        
        # Create directory
        if not os.path.exists(share_path):
            create = input(f"Path {share_path} doesn't exist. Create? (yes/no) [yes]: ").strip().lower() or "yes"
            if create == "yes":
                os.makedirs(share_path, exist_ok=True)
            else:
                sys.exit(1)
        
        # User management
        users = []
        if guest_ok == "no":
            while True:
                user = input("Enter username (empty to finish): ").strip()
                if not user:
                    break
                
                if not subprocess.run(f"id {user}", shell=True, stdout=subprocess.DEVNULL).returncode == 0:
                    create_user = input(f"User {user} doesn't exist. Create? (yes/no) [no]: ").strip().lower() or "no"
                    if create_user == "yes":
                        run_cmd(f"useradd -m -s /usr/sbin/nologin {user}")
                        run_cmd(f"passwd -l {user}")
                
                run_cmd(f"smbpasswd -L -a {user}")
                run_cmd(f"smbpasswd -L -e {user}")
                users.append(user)
        
        # Build config
        config = f"""\
[global]
   workgroup = WORKGROUP
   server role = standalone server
   security = user
   map to guest = bad user
   smb encrypt = required
   min protocol = SMB2_02
   unix password sync = yes

[{share_name}]
   path = {share_path}
   browseable = {browseable}
   writable = {writable}
   guest ok = {guest_ok}"""
        
        if guest_ok == "no" and users:
            config += f"\n   valid users = {' '.join(users)}"
        
        with open("/etc/samba/smb.conf", "w") as f:
            f.write(config)
        
        # Set permissions
        if guest_ok == "no" and users:
            run_cmd(f"chown -R {users[0]} {share_path}")
            run_cmd(f"chmod 2770 {share_path}")
        else:
            run_cmd(f"chmod 2777 {share_path}")
        
        # Restart services
        run_cmd("systemctl enable smbd")
        run_cmd("systemctl restart smbd")
        
        print("Setup complete!")
        print(f"Share: \\\\{os.uname().nodename}\\{share_name}")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
