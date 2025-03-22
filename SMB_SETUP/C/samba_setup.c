#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <time.h>

#define LOG_DIR "/var/log/samba_setup"
#define MAX_LOG_SIZE (5LLU * 1024LLU * 1024LLU * 1024LLU) // 5GB
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAX_INPUT 256
#define MAX_USERS 10

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
    
    // ... (similar input handling for other fields)
    
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
                    run_command("useradd -m -s /usr/sbin/nologin %s", user);
                    run_command("passwd -l %s", user);
                }
            }
            
            run_command("smbpasswd -L -a %s", user);
            run_command("smbpasswd -L -e %s", user);
            strcpy(users[user_count++], user);
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
    return 0;
}
