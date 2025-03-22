export_hashes() {
    if [ "$1" == "--export-hashes" ]; then
        echo "WARNING: Hash export should only be done for migration/backup"
        echo "Continue? (yes/no) [no]: "
        read confirm
        confirm=${confirm:-no}  # Default to "no" if input is empty
        if [ "${confirm,,}" == "yes" ]; then  # Case-insensitive comparison
            timestamp=$(date +%s)
            filename="/root/samba_hashes_${timestamp}.txt"
            pdbedit -L -w > "$filename"
            chmod 600 "$filename"
            echo "Hashes exported to $filename"
        fi
        exit 0  # Exit whether confirmed or not, matching original behavior
    fi
    # If flag is not present, return to caller
}
