Here is a `README.md` file for the `export_hashes` script:

```markdown
# Export Hashes Script

This script is designed to export Samba user hashes for migration or backup purposes. 

## Usage

To run the script, use the following command:

```sh
./export_hashes --export-hashes
```

### Warning

Exporting hashes should only be done for migration or backup purposes. Be cautious with the exported hash file as it contains sensitive information.

## Script Details

- **Function**: `export_hashes`
- **Parameter**: `--export-hashes`

### How It Works

1. The script checks if the `--export-hashes` flag is present.
2. If the flag is present, it prompts a warning and asks for confirmation to continue.
3. If the user confirms with "yes", the script:
   - Generates a timestamp.
   - Creates a filename `/root/samba_hashes_<timestamp>.txt`.
   - Exports the Samba user hashes using `pdbedit -L -w` and saves them to the file.
   - Sets the file permissions to `600` to ensure it's readable and writable only by the root user.
   - Outputs a message indicating the file location.
4. The script exits after the operation, whether the user confirmed or not.

### Example

To export the hashes:

```sh
./export_hashes --export-hashes
```

Upon running the command, you will see a warning and be prompted to confirm the export:

```sh
WARNING: Hash export should only be done for migration/backup
Continue? (yes/no) [no]: yes
Hashes exported to /root/samba_hashes_<timestamp>.txt
```
```

Replace `<timestamp>` with the actual timestamp value generated during the script execution.

This README.md file should provide a clear understanding of the `export_hashes` script and its usage.
