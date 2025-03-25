rom enum import Enum
from impacket.smbconnection import SMBConnection
from impacket.dcerpc.v5 import wkst, srvs

# This script uses the Impacket library for SMB and RPC enumeration.
# Impacket is a powerful Python library that provides low-level access to network protocols,
# making it an essential tool for penetration testers and security researchers.
# In this script, we use Impacket to enumerate information from a target system
# based on the intensity level selected by the user.

# Define intensity levels using Enum
class IntensityLevel(Enum):
    LOW = 1       # Basic enumeration (e.g., listing SMB shares)
    MEDIUM = 2    # Intermediate enumeration (e.g., enumerating logged-on users)
    HIGH = 3      # Advanced enumeration (e.g., sessions, services, and vulnerabilities)

def enumerate_users(target, username, password, domain, intensity):
    """
    Function to perform enumeration on a target system based on the selected intensity level.
    
    Parameters:
        target (str): The IP address or hostname of the target system.
        username (str): The username for authentication.
        password (str): The password for authentication.
        domain (str): The domain for authentication.
        intensity (IntensityLevel): The level of enumeration to perform.
    """
    try:
        # Establish an SMB connection to the target system
        conn = SMBConnection(target, target)
        conn.login(username, password, domain)

        # Perform enumeration based on the selected intensity level
        if intensity == IntensityLevel.LOW:
            print("Performing basic enumeration...")
            # LOW INTENSITY: List SMB shares available on the target system
            shares = conn.listShares()
            print("\n[+] Shares found:")
            for share in shares:
                print(f"  - {share['shi1_netname']}")
        
        elif intensity == IntensityLevel.MEDIUM:
            print("Performing medium enumeration...")
            # MEDIUM INTENSITY: Enumerate logged-on users using RPC calls
            dce = conn.getDCE()  # Get a DCE/RPC connection object from the SMB connection
            dce.connect()  # Establish the DCE/RPC connection
            dce.bind(wkst.MSRPC_UUID_WKST)  # Bind to the Workstation service UUID
            
            # Send a request to enumerate logged-on users
            request = wkst.NetrWkstaUserEnum()
            response = dce.request(request)
            
            print("\n[+] Logged-on users found:")
            for user in response['UserInfo']['WkstaUserInfo']:
                print(f"  - {user['wkui1_username']}")
        
        elif intensity == IntensityLevel.HIGH:
            print("Performing advanced enumeration...")
            
            # HIGH INTENSITY: Perform advanced enumeration tasks
            
            # Enumerate active sessions on the target machine
            print("\n[+] Enumerating active sessions...")
            try:
                dce = conn.getDCE()
                dce.connect()
                dce.bind(srvs.MSRPC_UUID_SRVS)  # Bind to Server service UUID
                
                request = srvs.NetrSessionEnum()
                response = dce.request(request)
                
                if response['SessionInfo']['Level'] == 10:  # Check session info level
                    sessions = response['SessionInfo']['SessionInfo10']
                    for session in sessions:
                        print(f"  - User: {session['sesi10_username']}, "
                              f"Client: {session['sesi10_cname']}, "
                              f"Active Time: {session['sesi10_time']}")
                else:
                    print("No active sessions found.")
            
            except Exception as e:
                print(f"Error enumerating sessions: {e}")
            
            # Check for writable or potentially exploitable shares
            print("\n[+] Checking writable/exploitable shares...")
            try:
                shares = conn.listShares()
                for share in shares:
                    share_name = share['shi1_netname']
                    if not share_name.endswith('$'):  # Skip administrative shares
                        try:
                            conn.listPath(share_name, '*')
                            print(f"  - Share '{share_name}' is accessible.")
                        except Exception as e:
                            print(f"  - Share '{share_name}' is not accessible: {e}")
            
            except Exception as e:
                print(f"Error checking writable shares: {e}")
            
            # Enumerate services running on the target system (if applicable)
            print("\n[+] Enumerating services (requires additional privileges)...")
            try:
                dce.bind(srvs.MSRPC_UUID_SRVS)
                request = srvs.NetrServerGetInfo()  # Example request to get server info
                response = dce.request(request)
                
                server_info = response['ServerInfo']['ServerName']
                print(f"Server Name: {server_info}")
            
            except Exception as e:
                print(f"Error enumerating services: {e}")
        
        else:
            print("Invalid intensity level selected.")
        
        conn.close()  # Close the SMB connection after completing enumeration

    except Exception as e:
        print(f"Error during enumeration: {e}")

if __name__ == "__main__":
    """
    Main function to prompt the user for input and initiate enumeration.
    """
    # Example usage: Replace these values with your actual target and credentials
    target_ip = "192.168.1.1"  # Target IP address or hostname
    user = "admin"             # Username for authentication
    pwd = "password"           # Password for authentication
    domain_name = "WORKGROUP"  # Domain name (use WORKGROUP if not part of a domain)
    
    print("Select intensity level:")
    for level in IntensityLevel:
        print(f"{level.value}. {level.name}")
    
    selected_level = int(input("Enter your choice: "))
    
    try:
        # Convert user input into an IntensityLevel enum value
        intensity_level = IntensityLevel(selected_level)
        
        # Call the enumerate_users function with the selected intensity level
        enumerate_users(target_ip, user, pwd, domain_name, intensity_level)
    
    except ValueError:
        print("Invalid selection. Please choose a valid intensity level.")
