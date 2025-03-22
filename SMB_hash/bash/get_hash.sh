# Capture hashes without exporting
hashes=$(get_hashes_and_export)
echo "$hashes"

# Export hashes with flag
get_hashes_and_export --export-hashes
