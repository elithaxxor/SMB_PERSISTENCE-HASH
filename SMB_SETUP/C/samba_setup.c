#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <time.h>

#define LOG_DIR "/var/log/samba_setup"
#define MAX_LOG_SIZE (5LLU * 1024LLU * 1024LLU * 1024LLU) // 5GB

void setup_logging() {
    struct stat st = {0};
    if (stat(LOG_DIR, &st) == -1) {
        mkdir(LOG_DIR, 0700);
    }
    
    // Check existing log size
    FILE *log_file = fopen(LOG_FILE, "a+");
    if (log_file) {
        fseek(log_file, 0L, SEEK_END);
        if (ftell(log_file) > MAX_LOG_SIZE) {
            remove(LOG_FILE);
        }
        fclose(log_file);
    }
}

void log_message(const char *type, const char *color, const char *message) {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    
    printf("%s%s%s [%02d:%02d:%02d] %s\n", 
        color, type, COLOR_RESET,
        t->tm_hour, t->tm_min, t->tm_sec,
        message);
    
    FILE *log_file = fopen(LOG_FILE, "a");
    if (log_file) {
        fprintf(log_file, "[%04d-%02d-%02d %02d:%02d:%02d] %s %s\n",
            t->tm_year + 1900, t->tm_mon + 1, t->tm_mday,
            t->tm_hour, t->tm_min, t->tm_sec,
            type, message);
        fclose(log_file);
    }
}

// Usage example:
log_message("[+]", COLOR_GREEN, "Successfully installed Samba");
log_message("[-]", COLOR_RED, "Installation failed: Permission denied");
log_message("[!]", COLOR_YELLOW, "Checking network connectivity...");
