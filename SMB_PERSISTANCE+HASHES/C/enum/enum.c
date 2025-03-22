#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // Define target network and log file names
    char network[] = "192.168.1.0/24";
    char hostsLog[] = "smb_hosts.log";
    char enumLog[]  = "smb_enum.log";
    char hashesLog[] = "ntlm_hashes.log";
    FILE *fp;
    char cmd[512];
    char line[256];
    
    // 1. Install required tools if not present
    const char* tools[] = {"nmap", "smbclient", "rpcclient", "enum4linux", "crackmapexec", "smbmap"};
    size_t tool_count = sizeof(tools)/sizeof(tools[0]);
    for (size_t i = 0; i < tool_count; ++i) {
        snprintf(cmd, sizeof(cmd), "which %s >/dev/null 2>&1 || (echo \"Installing %s...\" && apt-get update -y && apt-get install -y %s)", tools[i], tools[i], tools[i]);
        system(cmd);
    }
    
    // 2. Scan network for SMB hosts using nmap
    printf("[*] Scanning network %s for SMB hosts...\n", network);
    snprintf(cmd, sizeof(cmd), "nmap -p139,445 --open -Pn -n -oG smb_scan.txt %s >/dev/null 2>&1", network);
    system(cmd);
    
    // Open the nmap grepable output and find host IPs
    fp = fopen("smb_scan.txt", "r");
    if (!fp) {
        perror("[!] Unable to open nmap output");
        return 1;
    }
    FILE *hostsFile = fopen(hostsLog, "w");
    if (!hostsFile) {
        perror("[!] Unable to create hosts log");
        return 1;
    }
    fprintf(hostsFile, "SMB hosts discovered on %s:\n", network);
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, "Ports:") && (strstr(line, "139/open") || strstr(line, "445/open"))) {
            // Extract IP address from the line
            char *ip = strtok(line, " ");
            if (ip) {
                fprintf(hostsFile, "%s\n", ip); // log the IP
            }
        }
    }
    fclose(fp);
    fclose(hostsFile);
    
    // 3. Enumerate each host found
    hostsFile = fopen(hostsLog, "r");
    FILE *enumFile = fopen(enumLog, "w");
    FILE *hashFile = fopen(hashesLog, "w");
    if (!hostsFile || !enumFile || !hashFile) {
        perror("[!] Unable to open log file for writing");
        return 1;
    }
    char ip[64];
    // Skip the first line in hostsFile (header)
    fgets(line, sizeof(line), hostsFile);
    while (fgets(ip, sizeof(ip), hostsFile)) {
        // Remove newline from IP string
        ip[strcspn(ip, "\n")] = 0;
        if(strlen(ip) < 7) continue; // skip empty or invalid lines
        
        fprintf(enumFile, "\n===== Enumeration for host %s =====\n", ip);
        
        // a. NetBIOS workgroup/domain and names
        snprintf(cmd, sizeof(cmd), "nmblookup -A %s 2>/dev/null", ip);
        fprintf(enumFile, "[*] NetBIOS Names for %s:\n", ip);
        fflush(enumFile);
        system(cmd); // output will be appended to enumFile via shell redirection below
        // Actually, to capture command output into our file, we might use popen for finer control.
        // For simplicity, let's use system with >> redirection:
        snprintf(cmd, sizeof(cmd), "nmblookup -A %s 2>/dev/null >> %s", ip, enumLog);
        system(cmd);
        
        // b. List shares with smbclient (anonymous)
        snprintf(cmd, sizeof(cmd), "smbclient -L \\\\%s -N -g 2>/dev/null >> %s", ip, enumLog);
        system(cmd);
        
        // c. Shares and access with smbmap
        snprintf(cmd, sizeof(cmd), "echo \"[*] smbmap for %s:\" >> %s", ip, enumLog);
        system(cmd);
        snprintf(cmd, sizeof(cmd), "smbmap -H %s -u \"guest\" -p \"\" 2>/dev/null >> %s", ip, enumLog);
        system(cmd);
        
        // d. RPC null session enumeration (users, groups)
        snprintf(cmd, sizeof(cmd), "echo \"[*] rpcclient (null session) for %s:\" >> %s", ip, enumLog);
        system(cmd);
        snprintf(cmd, sizeof(cmd), "rpcclient -U \"\" -N %s -c \"srvinfo; enumdomusers; enumdomgroups\" 2>/dev/null >> %s", ip, enumLog);
        system(cmd);
        
        // e. Comprehensive enum4linux
        snprintf(cmd, sizeof(cmd), "echo \"[*] enum4linux output for %s:\" >> %s", ip, enumLog);
        system(cmd);
        snprintf(cmd, sizeof(cmd), "enum4linux -a %s 2>/dev/null >> %s", ip, enumLog);
        system(cmd);
        
        // f. Search for NTLM hashes in the accumulated enum output for this host
        // (Using a simple pattern: 32 hex chars (LM hash) or 32 after a colon (NTLM) as in SAM hashes)
        FILE *tempEnum = fopen(enumLog, "r");
        if(tempEnum) {
            char enumLine[512];
            while(fgets(enumLine, sizeof(enumLine), tempEnum)) {
                // NTLM hashes often appear as 32 hex chars (128 bits) possibly separated by colon from username or RID
                if(strstr(enumLine, ":::") || strstr(enumLine, ":$")) {
                    // If the line looks like it contains hash data (e.g., in output of some tools)
                    fprintf(hashFile, "%s", enumLine);
                }
            }
            fclose(tempEnum);
        }
    }
    
    fclose(hostsFile);
    fclose(enumFile);
    fclose(hashFile);
    
    printf("[*] Enumeration complete. See %s and %s for details.\n", enumLog, hashesLog);
    return 0;
}
