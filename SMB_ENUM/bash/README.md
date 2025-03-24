# SMB Enumeration Scripts

This directory contains various scripts designed for enumerating SMB (Server Message Block) services on a network. These scripts are useful for network administrators, security professionals, and penetration testers who need to identify and analyze SMB shares, users, and potential vulnerabilities.

## Contents

- **`enum_II.sh`**: A comprehensive script for scanning the network for SMB hosts, enumerating workgroups/domains, users, shares, and attempting to retrieve NTLM hashes via null sessions or open shares.
- **`SMB_enum_IV.sh`**: Script to enumerate SMB shares and workgroups using tools like `nmap`, `enum4linux`, `smbclient`, and `smbmap`.
- **`smb_enum_III.sh`**: Similar to `SMB_enum_IV.sh`, this script enumerates SMB shares and workgroups using the same set of tools.

## Usage

### Prerequisites

Ensure that the following tools are installed on your system:

- `smbclient`
- `enum4linux`
- `nmap`
- `smbmap`
- `crackmapexec`
- `rpcclient`

### Running the Scripts

1. **Ensure you have root privileges**: Most scripts require root privileges to install tools and perform certain scans.

2. **Choose a script to run**:
    - **`enum_II.sh`**:
        ```bash
        sudo bash SMB_ENUM/bash/enum_II.sh
        ```
    - **`SMB_enum_IV.sh`**:
        ```bash
        sudo bash SMB_ENUM/bash/SMB_enum_IV.sh
        ```
    - **`smb_enum_III.sh`**:
        ```bash
        sudo bash SMB_ENUM/bash/smb_enum_III.sh
        ```

3. **Use the Interactive Wrapper**: An interactive script is available to choose and run any of the above scripts, including an option to run all of them concurrently.

    ```bash
    sudo bash SMB_ENUM/bash/interactive_smb_enum.sh
    ```

    The wrapper script provides an interactive menu:
    - Option 1: Run `enum_II.sh`
    - Option 2: Run `SMB_enum_IV.sh`
    - Option 3: Run `smb_enum_III.sh`
    - Option 4: Hail Mary (Run all scripts concurrently)
    - Option 5: Exit

### Example Commands

- **Running `enum_II.sh`**:
    ```bash
    sudo bash SMB_ENUM/bash/enum_II.sh
    ```

- **Running `SMB_enum_IV.sh`**:
    ```bash
    sudo bash SMB_ENUM/bash/SMB_enum_IV.sh
    ```

- **Running `smb_enum_III.sh`**:
    ```bash
    sudo bash SMB_ENUM/bash/smb_enum_III.sh
    ```

- **Using the Interactive Wrapper**:
    ```bash
    sudo bash SMB_ENUM/bash/interactive_smb_enum.sh
    ```

### Logs

Each script generates log files in the current directory, capturing the details of the enumeration process. Review these logs for detailed information about the discovered SMB services and potential vulnerabilities.

- `smb_hosts.log`: Log file for discovered SMB hosts.
- `smb_enum.log`: Log file for enumeration details.
- `ntlm_hashes.log`: Log file for NTLM hashes found.

## Contributions

Contributions to improve these scripts are welcome. Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.
