#### to run: 

```bash 
sudo apt-get install build-essential
gcc samba_setup.c -o samba_setup
sudo ./samba_setup
```

or
```code
./runc.sh
```

# SMB MANAGER.C 
--> It is a combo installer and auditor
```
# Python
sudo apt install python3-colorama
sudo python3 smb_manager.py --install  # Configuration mode
sudo python3 smb_manager.py --audit    # Enumeration mode

# C
gcc smb_manager.c -o smb_manager
sudo ./smb_manager --install
sudo ./smb_manager --audit
```
