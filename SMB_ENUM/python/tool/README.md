
```markdown
# SMB Enumeration Tools

This directory contains two Python scripts designed for enumerating SMB (Server Message Block) services on a network. These scripts can help you discover workgroups, users, shares, and attempt to retrieve NTLM hashes from SMB hosts.

## Scripts

### 1. `smb_enum.py`

The `smb_enum.py` script is a comprehensive tool for SMB enumeration. It performs the following tasks:

- Discovers SMB hosts on the network using nmap.
- Enumerates workgroups/domains and users.
- Lists available shares on discovered hosts.
- Attempts to retrieve NTLM hashes.

**Pros:**
- Comprehensive enumeration including hosts, users, shares, and NTLM hashes.
- Uses multiple tools (nmap, crackmapexec, smbclient, enum4linux) for thorough scanning.
- Logs results to plaintext files, providing a record of the enumeration.

**Cons:**
- Requires several external tools (nmap, crackmapexec, smbclient, enum4linux) to be installed.
- More complex and potentially slower due to the comprehensive nature and multiple steps.

### 2. `smb_enum_II.py`

The `smb_enum_II.py` script is a simpler and more focused tool for SMB enumeration. It performs the following tasks:

- Discovers workgroups using `nmblookup`.
- Enumerates users in discovered workgroups using `rpcclient`.
- Extracts SMB hashes using `pdbedit`.

**Pros:**
- Simple and straightforward, focusing on key enumeration tasks.
- Requires fewer external tools, making it easier to set up and run.
- Faster execution due to fewer steps and tools involved.

**Cons:**
- Less comprehensive than `smb_enum.py`, focusing only on workgroups, users, and hashes.
- May miss some of the detailed information that `smb_enum.py` can gather.

## Choosing the Right Script

### When to Use `smb_enum.py`

- When you need a thorough and detailed enumeration of SMB services, including hosts, users, shares, and NTLM hashes.
- When you have the required external tools installed and are willing to wait for a more comprehensive scan.

### When to Use `smb_enum_II.py`

- When you need a quick and simple enumeration focusing on workgroups, users, and hashes.
- When you prefer a script with fewer dependencies and faster execution.

Both scripts provide valuable information for SMB enumeration, and the choice depends on your specific needs and setup.

## Running the Scripts

To run either script, simply execute it with Python:

```bash
python3 smb_enum.py
```

or

```bash
python3 smb_enum_II.py
```

Feel free to adjust the content as needed to better fit your project's requirements.
