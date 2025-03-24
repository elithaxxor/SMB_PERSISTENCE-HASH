import asyncio
from concurrent.futures import ThreadPoolExecutor
import subprocess
import aiofiles

NETWORK = "192.168.1.0/24"
HOSTS_LOG = "smb_hosts.log"
ENUM_LOG = "smb_enum.log"
HASHES_LOG = "ntlm_hashes.log"

# Function to run shell commands asynchronously
async def run_command(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode(), stderr.decode()

# Function to install required tools
async def install_tools():
    tools = ["nmap", "smbclient", "rpcclient", "enum4linux", "crackmapexec", "smbmap"]
    tasks = [run_command(f"apt-get install -y {tool}") for tool in tools]
    results = await asyncio.gather(*tasks)
    for stdout, stderr in results:
        if stderr:
            print(f"Error installing tool: {stderr}")

# Function to scan the network for SMB hosts
async def scan_network():
    stdout, stderr = await run_command(f"nmap -p 445 --script smb-enum-shares,smb-enum-users {NETWORK}")
    if stderr:
        print(f"Error scanning network: {stderr}")
    async with aiofiles.open("smb_enum_results.txt", mode='w') as f:
        await f.write(stdout)

# Function to enumerate SMB hosts
async def enumerate_host(ip):
    async with aiofiles.open(ENUM_LOG, mode='a') as f:
        await f.write(f"\n===== Enumerating host {ip} =====\n")
        commands = [
            f"nmblookup -A {ip}",
            f"smbclient -L //{ip}/ -N -g",
            f"smbmap -H {ip} -u 'guest' -p ''",
            f"rpcclient -U '' -N {ip} -c 'srvinfo; enumdomusers; enumdomgroups'",
            f"enum4linux -a {ip}",
            f"crackmapexec smb {ip} --gen-relay-list tmp_cme.txt"
        ]
        for command in commands:
            stdout, stderr = await run_command(command)
            await f.write(stdout)
            if stderr:
                print(f"Error running {command}: {stderr}")

# Function to read IPs from nmap scan results
async def get_smb_hosts():
    async with aiofiles.open("smb_enum_results.txt", mode='r') as f:
        content = await f.read()
        return [line.split()[1] for line in content.splitlines() if "open" in line]

# Main function to run the script
async def main():
    await install_tools()
    await scan_network()
    smb_hosts = await get_smb_hosts()
    if smb_hosts:
        tasks = [enumerate_host(ip) for ip in smb_hosts]
        await asyncio.gather(*tasks)
    print(f"[*] SMB enumeration complete. See {ENUM_LOG} for details and {HASHES_LOG} for any NTLM hashes.")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
