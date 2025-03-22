# Bash SMB Enumeration Script

## Overview:

#### The Bash script leverages common SMB enumeration tools and Linux commands to scan the LAN, discover SMB hosts and workgroups/domains, enumerate users and shares, and attempt to retrieve NTLM hashes via anonymous (null session) connections or open shares. It automatically installs any missing tools and stores results (including any NTLM hashes found) in plain text log files for later analysis. This script assumes it’s run on a Linux admin workstation (e.g., Kali) with sudo privileges for installing packages.

## Approach:

	1.	Network Scan: The script uses nmap to identify live hosts with SMB ports (139/TCP and 445/TCP) open on the local subnet. Nmap’s SMB NSE scripts (like smb-enum-shares) can quickly find share names even anonymously ￼.
	2.	Workgroup/Domain Discovery: For each discovered SMB host, it uses tools like nmblookup (NetBIOS name lookup) or crackmapexec to find the NetBIOS workgroup or AD domain names. For example, CrackMapExec can map live hosts in a subnet and report their names and domain membership ￼.
	3.	Share Enumeration: Using smbclient (with no password or as guest) and smbmap, the script lists available shares on each host. This distinguishes shares accessible anonymously vs those requiring credentials.
	4.	User Enumeration: The script tries to gather user accounts from each host. It uses rpcclient with a null session (-U "" -N) to run RPC calls like enumdomusers or RID cycling. On misconfigured systems, null sessions can list user accounts (by RID) ￼. The script may also invoke enum4linux (a wrapper around Samba tools ￼ that automates user, share, and OS enumeration) for thorough results.
	5.	NTLM Hash Retrieval: If possible, the script attempts to retrieve password hashes. This could involve mounting open shares that contain sensitive files (e.g., grabbing SAM database files from a misconfigured share) or using rpcclient/samrdump to extract user password hashes via SAMR if the host allows it. It may also utilize crackmapexec to perform additional enumeration or known techniques (e.g., RID brute force) to retrieve NTLM hashes if available ￼. All collected NTLM hashes are saved into an unprotected text log (for demonstration, not a security best practice).
	6.	Logging: The script writes outputs to log files (e.g., smb_hosts.log for discovered hosts, smb_enum.log for enumeration details, and ntlm_hashes.log for captured hashes). These files are stored with open permissions (world-readable) to simulate the “unprotected plain text” requirement
