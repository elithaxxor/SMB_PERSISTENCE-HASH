#ifndef HASH_EXTRACT_H
#define HASH_EXTRACT_H

typedef struct {
    char username[256];
    char uid[16];
    char nt_hash[65];
} SmbHash;

SmbHash* extract_smb_hashes(int *count);
void free_hashes(SmbHash *hashes, int count);
void display_hashes(SmbHash *hashes, int count);

#endif
