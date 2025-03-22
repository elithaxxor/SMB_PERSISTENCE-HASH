#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>

#define MAX_INPUT 256

void export_hashes(int argc, char *argv[]) {
    if (argc > 1 && strcmp(argv[1], "--export-hashes") == 0) {
        printf("WARNING: Hash export should only be done for migration/backup\n");
        printf("Continue? (yes/no) [no]: ");
        char confirm[MAX_INPUT];
        fgets(confirm, MAX_INPUT, stdin);
        confirm[strcspn(confirm, "\n")] = 0;  // Remove trailing newline
        
        // Convert input to lowercase for case-insensitive comparison
        for (char *p = confirm; *p; p++) {
            *p = tolower(*p);
        }
        
        if (strcmp(confirm, "yes") == 0) {
            time_t t = time(NULL);
            char filename[MAX_INPUT];
            snprintf(filename, MAX_INPUT, "/root/samba_hashes_%ld.txt", t);
            
            char cmd[MAX_INPUT * 2];
            snprintf(cmd, sizeof(cmd), "pdbedit -L -w > %s", filename);
            system(cmd);
            
            snprintf(cmd, sizeof(cmd), "chmod 600 %s", filename);
            system(cmd);
            
            printf("Hashes exported to %s\n", filename);
        }
        exit(0);  // Exit whether confirmed or not
    }
    // If flag is not present, return to caller
}
