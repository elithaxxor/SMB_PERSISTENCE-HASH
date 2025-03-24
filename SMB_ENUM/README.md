# SMB Enumeration Framework

This directory contains Python scripts and shell tools designed for enumerating SMB (Server Message Block) services on a network. The scripts help discover workgroups, users, shares, and attempt to retrieve NTLM hashes from SMB hosts.

## Directory Structure

- `main.py`: The main wrapper script that provides an interactive menu to run the individual tools or all tools at once.
- `tools/`: Directory containing the enumeration scripts.
  - `smb_enum.py`: A comprehensive Python script for SMB enumeration.
  - `smb_enum_II.py`: A simpler and more focused Python script for SMB enumeration.
  - `README.md`: This file, providing an overview of the tools and their usage.

## Scripts Overview

### `main.py`

The `main.py` script is an interactive menu-driven wrapper that allows users to select which enumeration tool to run or to run all tools sequentially. It uses the `curses` library to provide a text-based user interface.

### `smb_enum.py`

The `smb_enum.py` script performs comprehensive SMB enumeration. It includes:

- Discovering SMB hosts on the network using nmap.
- Enumerating workgroups/domains and users.
- Listing available shares on discovered hosts.
- Attempting to retrieve NTLM hashes.

**Pros:**
- Comprehensive enumeration including hosts, users, shares, and NTLM hashes.
- Uses multiple tools (nmap, crackmapexec, smbclient, enum4linux) for thorough scanning.
- Logs results to plaintext files, providing a record of the enumeration.

**Cons:**
- Requires several external tools (nmap, crackmapexec, smbclient, enum4linux) to be installed.
- More complex and potentially slower due to the comprehensive nature and multiple steps.

### `smb_enum_II.py`

The `smb_enum_II.py` script is a simpler and more focused tool for SMB enumeration. It includes:

- Discovering workgroups using `nmblookup`.
- Enumerating users in discovered workgroups using `rpcclient`.
- Extracting SMB hashes using `pdbedit`.

**Pros:**
- Simple and straightforward, focusing on key enumeration tasks.
- Requires fewer external tools, making it easier to set up and run.
- Faster execution due to fewer steps and tools involved.

**Cons:**
- Less comprehensive than `smb_enum.py`, focusing only on workgroups, users, and hashes.
- May miss some of the detailed information that `smb_enum.py` can gather.

## Shell Tools Overview

The Python scripts mentioned above leverage several shell tools for their operation:

- `nmap`: Used for network discovery and identifying hosts with SMB services.
- `crackmapexec`: Used for SMB enumeration, retrieving information about domains, users, and attempting hash dumps.
- `smbclient`: Used for listing shares and interacting with SMB services.
- `enum4linux`: Used for enumerating information from Windows and Samba systems.
- `rpcclient`: Used for querying information from Windows and Samba systems.
- `pdbedit`: Used for extracting SMB hashes.

### Differences Between Python Tools and Shell Tools

**Python Tools:**
- Provide a higher-level interface and can integrate multiple shell tools.
- Easier to extend and modify for specific needs.
- Can handle complex logic and multiple steps in a single script.

**Shell Tools:**
- Directly interact with SMB services and perform specific tasks.
- Often faster and more efficient for individual tasks.
- Require manual integration and scripting for complex workflows.

## Choosing the Right Tool

- Use `smb_enum.py` when you need detailed and comprehensive enumeration.
- Use `smb_enum_II.py` for quick and focused enumeration tasks.
- Utilize the shell tools directly for specific tasks or when integrating into other scripts.

## Running the Scripts

To run the main interactive script:

```bash
python3 main.py
```

To run individual scripts:

```bash
python3 tools/smb_enum.py
python3 tools/smb_enum_II.py
```

Ensure you have the necessary permissions (root privileges) and that the required tools and libraries are installed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

Feel free to adjust the content as needed to better fit your project's requirements.
