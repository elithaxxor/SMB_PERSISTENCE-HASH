import subprocess
import threading
from smb.SMBConnection import SMBConnection
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def smb_enum_with_nmap(target_ip, intensity):
    """Enumerate SMB shares using Nmap."""
    logging.info(f"Running Nmap SMB enumeration on {target_ip} with intensity level {intensity}...")
    nmap_command = ["nmap", "-p", "139,445", "--script", "smb-enum-shares.nse,smb-enum-users.nse", target_ip]
    
    # Add aggressive options for higher intensity
    if intensity == "high":
        nmap_command += ["-T4", "-A"]

    try:
        result = subprocess.run(nmap_command, stdout=subprocess.PIPE, text=True, check=True)
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running Nmap: {e}")

def smb_enum_with_smbmap(target_ip, username=None, password=None, intensity="low"):
    """Enumerate SMB shares using smbmap."""
    logging.info(f"Running SMBMap enumeration on {target_ip} with intensity level {intensity}...")
    smbmap_command = ["smbmap", "-H", target_ip]
    
    # Add credentials if provided
    if username and password:
        smbmap_command += ["-u", username, "-p", password]

    # Add deeper checks for higher intensity
    if intensity == "high":
        smbmap_command += ["-r"]  # Recursively list files

    try:
        result = subprocess.run(smbmap_command, stdout=subprocess.PIPE, text=True, check=True)
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running SMBMap: {e}")

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
    finally:
        conn.close()

def run_enumeration(target_ip, username=None, password=None, intensity="low"):
    """Run enumeration based on the specified intensity level."""
    if intensity not in ["low", "medium", "high"]:
        logging.error("Invalid intensity level! Choose from 'low', 'medium', or 'high'.")
        return

    threads = []

    # Low Intensity: Basic Nmap scan
    if intensity == "low":
        threads.append(threading.Thread(target=smb_enum_with_nmap, args=(target_ip, intensity)))

    # Medium Intensity: Add SMBMap and authenticated checks
    elif intensity == "medium":
        threads.append(threading.Thread(target=smb_enum_with_nmap, args=(target_ip, intensity)))
        threads.append(threading.Thread(target=smb_enum_with_smbmap, args=(target_ip, username, password)))

    # High Intensity: Add PySMB and aggressive scans
    elif intensity == "high":
        threads.append(threading.Thread(target=smb_enum_with_nmap, args=(target_ip, intensity)))
        threads.append(threading.Thread(target=smb_enum_with_smbmap, args=(target_ip, username, password, intensity)))
        threads.append(threading.Thread(target=smb_enum_with_pysmb, args=(target_ip, username, password)))

    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Target IP address
    target_ip = "192.168.1.100"

    # Credentials for authenticated enumeration (if available)
    username = "guest"
    password = ""

    # Select the desired intensity level ('low', 'medium', 'high')
    intensity_level = "medium"

    # Run the enumeration process with the selected intensity level
    logging.info(f"Starting SMB enumeration on {target_ip} with '{intensity_level}' intensity.")
    run_enumeration(target_ip=target_ip, username=username, password=password, intensity=intensity_level)
