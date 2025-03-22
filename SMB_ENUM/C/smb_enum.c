#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXBUF 4096

void check_root() {
    if (geteuid() != 0) {
        fprintf(stderr, "[-] Must be run as root\n");
        exit(EXIT_FAILURE);
    }
}

void get_workgroups() {
    printf("[+] Discovering workgroups...\n");
    FILE *fp = popen("nmblookup -S __SAMBA__ | grep -oP '<GROUP>\\s+\\K\\S+' | sort -u", "r");
    char buffer[MAXBUF];
    
    printf("Workgroups:\n");
    while (fgets(buffer, MAXBUF, fp)) {
        printf(" - %s", buffer);
    }
    pclose(fp);
}

void enum_users() {
    printf("\n[+] Enumerating users...\n");
    system("for wg in $(nmblookup -S __SAMBA__ | grep -oP '<GROUP>\\s+\\K\\S+' | sort -u); do "
           "echo \"=== Workgroup: $wg ===\"; "
           "rpcclient -U% -W \"$wg\" -c \"enumdomusers\" 127.0.0.1 2>/dev/null | "
           "grep -oP '\\[.*?\\]' | tr -d '[]'; done | sort -u");
}

void extract_hashes() {
    printf("\n[+] SMB Hashes:\n");
    system("pdbedit -L -w | grep -v ':\\$' | column -t -s:");
}

int main() {
    check_root();
    get_workgroups();
    enum_users();
    extract_hashes();
    return 0;
}
