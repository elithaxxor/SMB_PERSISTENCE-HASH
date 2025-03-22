import subprocess
import threading
import multiprocessing
from smb.SMBConnection import SMBConnection
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def smb_enum_with_nmap(target_ip):
    """Enumerate SMB shares using Nmap."""
    logging.info(f"Running Nmap SMB enumeration on {target_ip}...")
    nmap_command = ["nmap", "-p", "139,445", "--script", "smb-enum-shares.nse,smb-enum-users.nse", target_ip]
    try:
        result = subprocess.run(nmap_command, stdout=subprocess.PIPE, text=True, check=True)
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running Nmap: {e}")
        print(f"Error running Nmap: {e}")

def smb_enum_with_smbmap(target_ip, username=None, password=None):
    """Enumerate SMB shares using smbmap."""
    logging.info(f"Running SMBMap enumeration on {target_ip}...")
    smbmap_command = ["smbmap", "-H", target_ip]
    if username and password:
        smbmap_command += ["-u", username, "-p", password]
    try:
        result = subprocess.run(smbmap_command, stdout=subprocess.PIPE, text=True, check=True)
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running SMBMap: {e}")
        print(f"Error running SMBMap: {e}")

def smb_enum_with_pysmb(target_ip, username, password):
    """Enumerate SMB shares using pysmb."""
    logging.info(f"Running PySMB enumeration on {target_ip}...")
    conn = SMBConnection(username, password, "my_machine", target_ip, use_ntlm_v2=True)
    try:
        conn.connect(target_ip, 139)
        shares = conn.listShares()
        for share in shares:
            logging.info(f"Share: {share.name}, Comment: {share.comments}")
            print(f"Share: {share.name}, Comment: {share.comments}")
    except Exception as e:
        logging.error(f"Error connecting to SMB: {e}")
        print(f"Error connecting to SMB: {e}")
    finally:
        conn.close()

def run_all_enumerations(target_ip, username, password):
    """Run all enumeration methods in parallel."""
    threads = []
    # Nmap enumeration
    threads.append(threading.Thread(target=smb_enum_with_nmap, args=(target_ip,)))
    # SMBMap enumeration
    threads.append(threading.Thread(target=smb_enum_with_smbmap, args=(target_ip, username, password)))
    # PySMB enumeration
    threads.append(threading.Thread(target=smb_enum_with_pysmb, args=(target_ip, username, password)))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Target IP address
    target_ip = "192.168.1.100"

    # Credentials for authenticated enumeration (if available)
    username = "guest"
    password = ""

    # Run all enumerations in parallel using threading
    run_all_enumerations(target_ip, username, password)
