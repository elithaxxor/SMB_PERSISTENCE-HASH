## SMB PERSISTANCE W, HASH GRAB (Your settting up the server and want whatever hashes are created) or existing) 

# Python
sudo apt install python3-colorama
sudo python3 smb_manager.py --install  # Configuration mode
sudo python3 smb_manager.py --audit    # Enumeration mode

# C
gcc smb_manager.c -o smb_manager
sudo ./smb_manager --install
sudo ./smb_manager --audit


#### Change Log: --> This is the code used to grep the SMB hashes

```bash
/*
Build the program: make
Clean build files: make clean
Install system-wide: sudo make install
Uninstall: sudo make uninstall
*/
```



```c

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
```
