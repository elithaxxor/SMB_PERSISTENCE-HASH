#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>

#define MAX_CMD 1024
#define LOG_FILE "/var/log/smb_manager.log"

void log_message(const char* type, const char* message) {
    FILE* log = fopen(LOG_FILE, "a");
    if (log) {
        fprintf(log, "[%s] %s\n", type, message);
        fclose(log);
    }
}

void check_root() {
    if (geteuid() != 0) {
        printf("[-] Requires root privileges\n");
        exit(EXIT_FAILURE);
    }
}

void install_samba() {
    system("apt-get update > /dev/null 2>&1");
    if (system("apt-get install -y samba > /dev/null 2>&1") != 0) {
        printf("[-] Samba installation failed\n");
        exit(EXIT_FAILURE);
    }
    system("cp /etc/samba/smb.conf /etc/samba/smb.conf.bak");
    printf("[+] Samba installed\n");
}

void configure_share() {
    char share_name[256], share_path[256];
    printf("[!] Enter share name: ");
    fgets(share_name, sizeof(share_name), stdin);
    printf("[!] Enter share path: ");
    fgets(share_path, sizeof(share_path), stdin);

    struct stat st;
    if (stat(share_path, &st) == -1) {
        printf("[!] Create path? (y/N): ");
        char create;
        scanf("%c", &create);
        if (create == 'y' || create == 'Y') {
            char cmd[MAX_CMD];
            snprintf(cmd, MAX_CMD, "mkdir -p %s", share_path);
            system(cmd);
        }
    }

    FILE* conf = fopen("/etc/samba/smb.conf", "a");
    if (conf) {
        fprintf(conf, "[%s]n", share_name);
        fprintf(conf, "tpath = %s", share_path);
        fclose(conf);
    }
}

void enumerate_smb() {
    printf("[+] Discovering workgroups...\n");
    system("nmblookup -S __SAMBA__ | grep -oP '<GROUP>\\s+\\K\\S+'");
    
    printf("[+] Enumerating users...\n");
    system("for wg in $(nmblookup -S __SAMBA__ | grep -oP '<GROUP>\\s+\\K\\S+'); do "
           "rpcclient -U%% -W $wg -c 'enumdomusers' 127.0.0.1; done | grep -oP '\\[.*?\\]'");
    
    printf("[+] Extracting hashes...\n");
    system("pdbedit -L -w | grep -v ':\\$'");
}

int main(int argc, char *argv[]) {
    check_root();
    
    if (argc < 2) {
        printf("Usage: %s --install | --audit\n", argv[0]);
        return EXIT_FAILURE;
    }

    if (strcmp(argv[1], "--install") == 0) {
        install_samba();
        configure_share();
        // User management omitted for brevity
        system("systemctl restart smbd");
    }
    else if (strcmp(argv[1], "--audit") == 0) {
        enumerate_smb();
    }

    return EXIT_SUCCESS;
}
