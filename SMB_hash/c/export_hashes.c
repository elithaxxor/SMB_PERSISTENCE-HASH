#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>

#define BUFFER_SIZE 4096
#define MAX_INPUT 256

char* get_hashes_and_export(int argc, char *argv[]) {
    // Step 1: Retrieve hashes into memory
    FILE *fp = popen("pdbedit -L -w", "r");
    if (fp == NULL) {
        perror("popen failed");
        exit(1);
    }
    char buffer[BUFFER_SIZE];
    size_t len = fread(buffer, 1, BUFFER_SIZE - 1, fp);
    pclose(fp);
    buffer[len] = '\0'; // Null-terminate the string

    // Step 2: Check for export flag and handle export logic
    if (argc > 1 && strcmp(argv[1], "--export-hashes") == 0) {
        printf("WARNING: Hash export should only be done for migration/backup\n");
        printf("Continue? (yes/no) [no]: ");
        char confirm[MAX_INPUT];
        fgets(confirm, MAX_INPUT, stdin);
        confirm[strcspn(confirm, "\n")] = '\0'; // Remove newline
        for (char *p = confirm; *p; p++) *p = tolower(*p); // Convert to lowercase
        if (strcmp(confirm, "yes") == 0) {
            // Generate timestamped filename
            time_t t = time(NULL);
            char filename[MAX_INPUT];
            snprintf(filename, MAX_INPUT, "/root/samba_hashes_%ld.txt", t);

            // Write hashes to file
            FILE *out = fopen(filename, "w");
            if (out == NULL) {
                perror("fopen failed");
                exit(1);
            }
            fwrite(buffer, 1, len, out);
            fclose(out);

            // Set file permissions
            char cmd[MAX_INPUT * 2];
            snprintf(cmd, sizeof(cmd), "chmod 600 %s", filename);
            system(cmd);

            printf("Hashes exported to %s\n", filename);
        }
        exit(0); // Exit after handling export
    }

    // Step 3: Return hashes if no export
    char *result = malloc(len + 1);
    if (result == NULL) {
        perror("malloc failed");
        exit(1);
    }
    memcpy(result, buffer, len + 1);
    return result; // Caller must free this memory
}
