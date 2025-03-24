#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Log file
LOGFILE="interactive_smb_enum.log"

# Log function
log() {
    local type="$1"
    local message="$2"
    local color="$3"
    echo -e "${color}[${type}]${NC} ${message}" | tee -a "$LOGFILE"
}

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    log "!" "This script must be run as root (sudo)." "$YELLOW"
    exit 1
fi

# Install required tools
install_tools() {
    log "!" "Installing required tools..." "$YELLOW"
    apt-get install -y smbclient enum4linux nmap smbmap crackmapexec rpcclient
}

# Run enum_II.sh
run_enum_II() {
    log "+" "Running enum_II.sh..." "$GREEN"
    bash SMB_ENUM/bash/enum_II.sh
}

# Run SMB_enum_IV.sh
run_SMB_enum_IV() {
    log "+" "Running SMB_enum_IV.sh..." "$GREEN"
    bash SMB_ENUM/bash/SMB_enum_IV.sh
}

# Run smb_enum_III.sh
run_smb_enum_III() {
    log "+" "Running smb_enum_III.sh..." "$GREEN"
    bash SMB_ENUM/bash/smb_enum_III.sh
}

# Run all scripts concurrently
run_hail_mary() {
    log "+" "Running all scripts concurrently (Hail Mary)..." "$GREEN"
    
    # Run all scripts in parallel
    (
        run_enum_II &
        pid1=$!
        run_SMB_enum_IV &
        pid2=$!
        run_smb_enum_III &
        pid3=$!
        
        # Wait for all processes to finish
        wait $pid1
        wait $pid2
        wait $pid3
    )
}

# Display menu
show_menu() {
    echo "Interactive SMB Enumeration Menu"
    echo "1. Run enum_II.sh"
    echo "2. Run SMB_enum_IV.sh"
    echo "3. Run smb_enum_III.sh"
    echo "4. Hail Mary (Run all scripts concurrently)"
    echo "5. Exit"
}

# Main function
main() {
    install_tools

    while true; do
        show_menu
        read -p "Choose an option: " choice
        case $choice in
            1)
                run_enum_II
                ;;
            2)
                run_SMB_enum_IV
                ;;
            3)
                run_smb_enum_III
                ;;
            4)
                run_hail_mary
                ;;
            5)
                log "!" "Exiting the script." "$YELLOW"
                exit 0
                ;;
            *)
                log "-" "Invalid option, please try again." "$RED"
                ;;
        esac
    done
}

main "$@"
