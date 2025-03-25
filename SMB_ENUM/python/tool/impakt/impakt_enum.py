import logging
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
from impacket.smbconnection import SMBConnection
from impacket.dcerpc.v5 import transport, wkst, srvs, scmr
from enum import Enum
import getpass
import uuid  # For generating unique temporary filenames


''' Review and test this script in a controlled environment since these RPC calls typically require administrative privileges on the target. '''

# Define enumeration intensity levels
class IntensityLevel(Enum):
    LOW = 1      # Basic share enumeration
    MEDIUM = 2   # Adds logged-on users and writable share check
    HIGH = 3     # Full enumeration (sessions, services, etc.)

# Set up logger
logger = logging.getLogger("SMBEnum")
logger.setLevel(logging.DEBUG)

# Console handler: INFO and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(console_formatter)

# Rotating file handler: detailed DEBUG logs
file_handler = RotatingFileHandler("smb_enum.log", maxBytes=5_000_000, backupCount=3)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s")
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# SMB Enumeration functions
def list_shares(conn):
    """List available shares on the target."""
    try:
        shares = conn.listShares()
        logger.info(f"{conn.getRemoteHost()} - Shares:")
        for share in shares:
            share_name = share['shi1_netname'][:-1]  # Remove null terminator
            logger.info(f"  - {share_name}")
    except Exception as e:
        logger.exception(f"Error listing shares on {conn.getRemoteHost()}: {e}")

def check_writable_shares(conn):
    """Check for writable shares by attempting to create and delete a unique file."""
    try:
        shares = conn.listShares()
        for share in shares:
            share_name = share['shi1_netname'][:-1]
            # Skip administrative shares
            if share_name.endswith("$"):
                logger.info(f"{conn.getRemoteHost()} - Skipping admin share '{share_name}' for writable check.")
                continue
            # Generate a unique temporary filename to avoid collisions
            test_filename = f"temp_test_file_{uuid.uuid4().hex}.txt"
            try:
                # Attempt to create the file
                fid = conn.createFile(share_name, test_filename)
                # If successful, delete the file to clean up
                conn.deleteFile(share_name, test_filename)
                logger.info(f"{conn.getRemoteHost()} - Share '{share_name}' is writable.")
            except Exception as e:
                logger.info(f"{conn.getRemoteHost()} - Share '{share_name}' is not writable: {e}")
    except Exception as e:
        logger.exception(f"Error checking writable shares on {conn.getRemoteHost()}: {e}")

def enumerate_logged_on_users(conn):
    """
    Enumerate logged-on users using NetrWkstaUserEnum.
    Note: This typically requires administrative privileges.
    """
    dce = None
    try:
        stringbinding = r'ncacn_np:%s[\pipe\wkssvc]' % conn.getRemoteHost()
        rpctransport = transport.DCERPCTransportFactory(stringbinding)
        rpctransport.set_dport(445)
        dce = rpctransport.get_dce_rpc()
        dce.connect()
        dce.bind(wkst.MSRPC_UUID_WKST)
        resp = wkst.hNetrWkstaUserEnum(dce, 1)
        buffer = resp.get('UserInfo', {}).get('WkstaUserInfo', {}).get('Level1', {}).get('Buffer', [])
        if buffer:
            for user in buffer:
                username = user['wkui1_username'][:-1] if user['wkui1_username'] else "<empty>"
                logger.info(f"{conn.getRemoteHost()} - Logged-on user: {username}")
        else:
            logger.info(f"{conn.getRemoteHost()} - No logged-on users found.")
    except Exception as e:
        logger.exception(f"Error enumerating logged-on users on {conn.getRemoteHost()}: {e}")
    finally:
        if dce:
            try:
                dce.disconnect()
            except Exception:
                pass

def enumerate_sessions(conn):
    """
    Enumerate active SMB sessions using NetrSessionEnum.
    Note: This typically requires proper privileges.
    """
    dce = None
    try:
        stringbinding = r'ncacn_np:%s[\pipe\srvsvc]' % conn.getRemoteHost()
        rpctransport = transport.DCERPCTransportFactory(stringbinding)
        rpctransport.set_dport(445)
        dce = rpctransport.get_dce_rpc()
        dce.connect()
        dce.bind(srvs.MSRPC_UUID_SRVS)
        resp = srvs.hNetrSessionEnum(dce, None, None, 10)
        buffer = resp.get('InfoStruct', {}).get('SessionInfo', {}).get('Level10', {}).get('Buffer', [])
        if buffer:
            for session in buffer:
                username = session['sesi10_username'][:-1] if session['sesi10_username'] else "<empty>"
                client = session['sesi10_cname'][:-1] if session['sesi10_cname'] else "<empty>"
                logger.info(f"{conn.getRemoteHost()} - Session: User {username} from {client}")
        else:
            logger.info(f"{conn.getRemoteHost()} - No SMB sessions found.")
    except Exception as e:
        logger.exception(f"Error enumerating sessions on {conn.getRemoteHost()}: {e}")
    finally:
        if dce:
            try:
                dce.disconnect()
            except Exception:
                pass

def enumerate_services(conn):
    """
    Enumerate services via RPC using the Service Control Manager.
    Note: This typically requires administrative privileges.
    """
    dce = None
    try:
        stringbinding = r'ncacn_np:%s[\pipe\svcctl]' % conn.getRemoteHost()
        rpctransport = transport.DCERPCTransportFactory(stringbinding)
        rpctransport.set_dport(445)
        dce = rpctransport.get_dce_rpc()
        dce.connect()
        dce.bind(scmr.MSRPC_UUID_SCMR)
        resp = scmr.hROpenSCManagerW(dce)
        scHandle = resp['lpScHandle']
        services = scmr.hREnumServicesStatusW(dce, scHandle)
        buffer = services.get('InfoStruct', {}).get('ServiceInfo', {}).get('Level1', {}).get('Buffer', [])
        if buffer:
            for svc in buffer:
                svc_name = svc['lpServiceName'][:-1] if svc['lpServiceName'] else "<empty>"
                svc_state = svc['ServiceStatus']['dwCurrentState']
                logger.info(f"{conn.getRemoteHost()} - Service: {svc_name}, State: {svc_state}")
        else:
            logger.info(f"{conn.getRemoteHost()} - No services found.")
    except Exception as e:
        logger.exception(f"Error enumerating services on {conn.getRemoteHost()}: {e}")
    finally:
        if dce:
            try:
                dce.disconnect()
            except Exception:
                pass

def enumerate_target(target, username, password, domain, intensity):
    """
    Enumerate a single target based on the selected intensity level.
    Runs in a separate thread for each target.
    """
    try:
        conn = SMBConnection(target, target, sess_port=445)
        conn.login(username, password, domain)
        logger.info(f"{target} - Connected successfully.")
        
        # Basic share enumeration is always performed
        list_shares(conn)
        
        # For MEDIUM or higher, enumerate logged-on users and check writable shares
        if intensity.value >= IntensityLevel.MEDIUM.value:
            enumerate_logged_on_users(conn)
            check_writable_shares(conn)
        
        # For HIGH intensity, enumerate sessions and services
        if intensity.value >= IntensityLevel.HIGH.value:
            enumerate_sessions(conn)
            enumerate_services(conn)
        
        conn.close()
        logger.info(f"{target} - Connection closed.")
    except Exception as e:
        logger.exception(f"{target} - Error during enumeration: {e}")

if __name__ == "__main__":
    # Securely collect user credentials
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    domain = input("Enter domain: ")

    # Prompt user to select intensity level
    print("Select intensity level:")
    for level in IntensityLevel:
        print(f"{level.value}. {level.name}")
    while True:
        try:
            selected_level = int(input("Enter your choice: "))
            intensity = IntensityLevel(selected_level)
            break
        except ValueError:
            print("[-] Please enter a valid number.")

    # Read targets from file
    try:
        with open("targets.txt", "r") as f:
            targets = [line.strip() for line in f if line.strip()]
        if not targets:
            print("[-] No targets found in targets.txt")
            exit(1)
    except FileNotFoundError:
        print("[-] targets.txt not found")
        exit(1)
    
    max_threads = 10  # Adjust based on system/network capacity
    logger.info(f"Starting enumeration of {len(targets)} targets using {max_threads} threads.")
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [
            executor.submit(enumerate_target, target, username, password, domain, intensity)
            for target in targets
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Thread error: {e}")

    logger.info("Enumeration complete. Check smb_enum.log for detailed results.")
