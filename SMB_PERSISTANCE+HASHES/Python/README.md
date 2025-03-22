# Python
sudo apt install python3-colorama
sudo python3 smb_manager.py --install  # Configuration mode
sudo python3 smb_manager.py --audit    # Enumeration mode

# C
gcc smb_manager.c -o smb_manager
sudo ./smb_manager --install
sudo ./smb_manager --audit
