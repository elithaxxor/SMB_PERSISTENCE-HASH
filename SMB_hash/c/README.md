Here is a `README.md` file for the provided C code snippet:

```markdown
# SMB Hash Export Tool

This repository contains a tool for exporting SMB hashes. The tool is written in C and can be used to backup or migrate SMB hashes from a Samba server.

## Description

The `export_hashes` function exports the hashes of SMB users to a file in the `/root` directory. The function should be called with the `--export-hashes` flag. Note that this operation should only be done for migration or backup purposes.

## Usage

To use the tool, compile the code and run the executable with the `--export-hashes` flag:

```bash
gcc -o export_hashes export_hashes.c
./export_hashes --export-hashes
```

The tool will prompt you with a warning and ask for confirmation:

```
WARNING: Hash export should only be done for migration/backup
Continue? (yes/no) [no]:
```

Type `yes` to proceed with the export, or `no` to cancel.

## Implementation Details

The `export_hashes` function performs the following steps:

1. Checks if the `--export-hashes` flag is present.
2. Displays a warning and asks for confirmation.
3. If confirmed, generates a filename based on the current time and exports the hashes to this file using the `pdbedit` command.
4. Sets the file permissions to `600` to ensure that only the root user can read/write the file.
5. Displays the location of the exported file.

## Example

Here is an example of how to use the tool:

```bash
$ ./export_hashes --export-hashes
WARNING: Hash export should only be done for migration/backup
Continue? (yes/no) [no]: yes
Hashes exported to /root/samba_hashes_1616177267.txt
```
