# SMB Persistence and Hash Management

This repository contains tools for managing SMB (Server Message Block) persistence and hash management, implemented in multiple programming languages for flexibility and different use cases. For instance, SMB  passwords are stored in a hashed smb db 

## Features

- Secure SMB setup and configuration
- User management with password protection
- Service persistence configuration
- SMB password hash retrieval
- Multiple implementation options (Python, C, Bash)
- Configurable share permissions
- Guest access control

## Components

### Python Implementation
- `Python/samba_setup.py`: Python-based implementation for SMB setup and configuration
- Features modern error handling and logging
- Comprehensive hash retrieval using pdbedit

### C Implementation
- `C/samba_setup.c`: C-based implementation for low-level SMB management
- Efficient system-level operations
- Integrated hash extraction capabilities

### Bash Implementation
- `Bash/secure-samba-setup.sh`: Shell script for secure SMB setup and configuration
- Simple yet powerful implementation
- Built-in hash retrieval functionality

## Usage

Each implementation can be used based on your specific needs and environment. All implementations require root privileges.

1. Python Implementation:
   ```bash
   sudo python3 Python/samba_setup.py
   ```

2. C Implementation:
   ```bash
   gcc C/samba_setup.c -o samba_setup
   sudo ./samba_setup
   ```

3. Bash Implementation:
   ```bash
   sudo bash Bash/secure-samba-setup.sh
   ```

## Features in Detail

### SMB Setup
- Automated Samba installation
- Secure configuration defaults
- Backup of original configuration
- Custom share configuration

### User Management
- System user creation
- Samba user configuration
- Password management
- Access control lists

### Security Features
- Enforced SMB encryption
- Minimum protocol version requirements
- Guest access control
- Permission management

### Hash Management
- Retrieval of LM and NT hashes
- Secure hash storage
- User-specific hash extraction
- Compatible with common SMB tools

## Security Notice

This tool should be used responsibly and in compliance with your organization's security policies. The hash retrieval functionality is intended for legitimate system administration purposes only.

## Requirements

- Root/Administrator privileges
- Python 3.x (for Python implementation)
- GCC (for C implementation)
- Bash shell
- Samba package (auto-installed if missing)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
