#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAX_INPUT 256
#define MAX_USERS 10
#define MAX_HASH_LENGTH 64


/*
Build the program: make
Clean build files: make clean
Install system-wide: sudo make install
Uninstall: sudo make uninstall
*/




// Function to retrieve SMB hashes
void get_smb_hashes() {
    printf("\n[+] Retrieving SMB password hashes...\n");
    
    // Check if running as root
    if(geteuid() != 0) {
        fprintf(stderr, "Need root privileges to retrieve hashes\n");
        return;
    }

    // Use pdbedit to get user list and hashes
    FILE *fp = popen("pdbedit -L -w 2>/dev/null", "r");
    if(!fp) {
        fprintf(stderr, "Failed to execute pdbedit command\n");
        return;
    }

    char line[MAX_INPUT];
    int found = 0;
    printf("\nSMB Password Hashes:\n");
    
    while(fgets(line, sizeof(line), fp)) {
        char *username = strtok(line, ":");
        if(!username) continue;
        
        // Skip three fields to get to the hashes
        char *lm_hash = NULL;
        char *nt_hash = NULL;
        
        for(int i = 0; i < 3; i++) {
            char *field = strtok(NULL, ":");
            if(!field) break;
            if(i == 1) lm_hash = field;
            if(i == 2) nt_hash = field;
        }
        
        if(username && lm_hash && nt_hash) {
            printf("User: %s\n", username);
            printf("LM Hash: %s\n", lm_hash);
            printf("NT Hash: %s\n", nt_hash);
            printf("-------------------------------------------------\n");
            found = 1;
        }
    }
    
    if(!found) {
        printf("[-] No SMB hashes retrieved\n");
    }
    
    pclose(fp);
}

void run_command(const char *cmd) {
    printf("Executing: %s\n", cmd);
    if(system(cmd) != 0) {
        perror("Command failed");
        exit(EXIT_FAILURE);
    }
}

// Function to retrieve SMB hashes
void get_smb_hashes() {
    printf("\n[+] Retrieving SMB password hashes...\n");
    
    // Check if running as root
    if(geteuid() != 0) {
        fprintf(stderr, "Need root privileges to retrieve hashes\n");
        return;
    }

    // Use pdbedit to get user list and hashes
    FILE *fp = popen("pdbedit -L -w 2>/dev/null", "r");
    if(!fp) {
        fprintf(stderr, "Failed to execute pdbedit command\n");
        return;
    }

    char line[MAX_INPUT];
    int found = 0;
    printf("\nSMB Password Hashes:\n");
    
    while(fgets(line, sizeof(line), fp)) {
        char *username = strtok(line, ":");
        if(!username) continue;
        
        // Skip three fields to get to the hashes
        char *lm_hash = NULL;
        char *nt_hash = NULL;
        
        for(int i = 0; i < 3; i++) {
            char *field = strtok(NULL, ":");
            if(!field) break;
            if(i == 1) lm_hash = field;
            if(i == 2) nt_hash = field;
        }
        
        if(username && lm_hash && nt_hash) {
            printf("User: %s\n", username);
            printf("LM Hash: %s\n", lm_hash);
            printf("NT Hash: %s\n", nt_hash);
            printf("-------------------------------------------------\n");
            found = 1;
        }
    }
    
    if(!found) {
        printf("[-] No SMB hashes retrieved\n");
    }
    
    pclose(fp);
}

void run_command(const char *cmd) {
    printf("Executing: %s\n", cmd);
    if(system(cmd) != 0) {
        perror("Command failed");
        exit(EXIT_FAILURE);
    }
}

int main() {
    if(geteuid() != 0) {
        fprintf(stderr, "Must be run as root\n");
        exit(EXIT_FAILURE);
    }

    // Install dependencies
    run_command("apt-get update");
    run_command("apt-get install -y samba");
    run_command("cp /etc/samba/smb.conf /etc/samba/smb.conf.bak");

    char share_name[MAX_INPUT];
    char share_path[MAX_INPUT];
    char browseable[MAX_INPUT] = "no";
    char writable[MAX_INPUT] = "no";
    char guest_ok[MAX_INPUT] = "no";
    
    printf("Enter share name: ");
    fgets(share_name, MAX_INPUT, stdin);
    share_name[strcspn(share_name, "\n")] = 0;
    
    printf("Enter full path to share directory: ");
    fgets(share_path, MAX_INPUT, stdin);
    share_path[strcspn(share_path, "\n")] = 0;
    
    // Create directory
    if(access(share_path, F_OK) != 0) {
        char create[MAX_INPUT];
        printf("Path doesn't exist. Create? (yes/no) [yes]: ");
        fgets(create, MAX_INPUT, stdin);
        create[strcspn(create, "\n")] = 0;
        if(strlen(create) == 0 || strcasecmp(create, "yes") == 0) {
            char cmd[MAX_INPUT * 2];
            snprintf(cmd, sizeof(cmd), "mkdir -p %s", share_path);
            run_command(cmd);
        }
    }
    
    // User management
    char users[MAX_USERS][MAX_INPUT];
    int user_count = 0;
    
    if(strcasecmp(guest_ok, "no") == 0) {
        while(user_count < MAX_USERS) {
            char user[MAX_INPUT];
            printf("Enter username (empty to finish): ");
            fgets(user, MAX_INPUT, stdin);
            user[strcspn(user, "\n")] = 0;
            
            if(strlen(user) == 0) break;
            
            // Check if user exists
            char cmd[MAX_INPUT * 2];
            snprintf(cmd, sizeof(cmd), "id %s >/dev/null 2>&1", user);
            if(system(cmd) != 0) {
                char create[MAX_INPUT];
                printf("User doesn't exist. Create? (yes/no) [no]: ");
                fgets(create, MAX_INPUT, stdin);
                create[strcspn(create, "\n")] = 0;
                
                if(strcasecmp(create, "yes") == 0) {
                    snprintf(cmd, sizeof(cmd), "useradd -m -s /usr/sbin/nologin %s", user);
                    run_command(cmd);
                    snprintf(cmd, sizeof(cmd), "passwd -l %s", user);
                    run_command(cmd);
                    snprintf(cmd, sizeof(cmd), "smbpasswd -L -a %s", user);
                    run_command(cmd);
                    snprintf(cmd, sizeof(cmd), "smbpasswd -L -e %s", user);
                    run_command(cmd);
                    strcpy(users[user_count++], user);
                }
            }
        }
    }
    
    // Build config file
    FILE *fp = fopen("/etc/samba/smb.conf", "w");
    if(fp) {
        fprintf(fp, "[global]\n");
        fprintf(fp, "   workgroup = WORKGROUP\n");
        fprintf(fp, "   server role = standalone server\n");
        fprintf(fp, "   security = user\n");
        fprintf(fp, "   map to guest = bad user\n");
        fprintf(fp, "   smb encrypt = required\n");
        fprintf(fp, "   min protocol = SMB2_02\n");
        fprintf(fp, "   unix password sync = yes\n\n");
        fprintf(fp, "[%s]\n", share_name);
        fprintf(fp, "   path = %s\n", share_path);
        fprintf(fp, "   browseable = %s\n", browseable);
        fprintf(fp, "   writable = %s\n", writable);
        fprintf(fp, "   guest ok = %s\n", guest_ok);
        
        if(user_count > 0 && strcasecmp(guest_ok, "no") == 0) {
            fprintf(fp, "   valid users = ");
            for(int i = 0; i < user_count; i++) {
                fprintf(fp, "%s ", users[i]);
            }
            fprintf(fp, "\n");
        }
        
        fclose(fp);
    }
    
    // Set permissions
    if(user_count > 0 && strcasecmp(guest_ok, "no") == 0) {
        char cmd[MAX_INPUT * 2];
        snprintf(cmd, sizeof(cmd), "chown -R %s %s", users[0], share_path);
        run_command(cmd);
        snprintf(cmd, sizeof(cmd), "chmod 2770 %s", share_path);
        run_command(cmd);
    } else {
        char cmd[MAX_INPUT * 2];
        snprintf(cmd, sizeof(cmd), "chmod 2777 %s", share_path);
        run_command(cmd);
    }
    
    run_command("systemctl enable smbd");
    run_command("systemctl restart smbd");
    
    printf("Setup complete!\n");

    // Retrieve and display SMB hashes
    get_smb_hashes();
    
    return 0;
}
