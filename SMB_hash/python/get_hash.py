import subprocess
import sys
import time

def get_hashes_and_export():
    # Step 1: Retrieve hashes into memory
    try:
        hashes = subprocess.check_output(["pdbedit", "-L", "-w"], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running pdbedit: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Check for export flag and handle export logic
    if len(sys.argv) > 1 and sys.argv[1] == "--export-hashes":
        print("WARNING: Hash export should only be done for migration/backup")
        print("Continue? (yes/no) [no]: ", end="")
        confirm = input().strip().lower()
        if confirm == "yes":
            timestamp = int(time.time())
            filename = f"/root/samba_hashes_{timestamp}.txt"
            with open(filename, "w") as f:
                f.write(hashes)
            subprocess.run(["chmod", "600", filename])
            print(f"Hashes exported to {filename}")
        sys.exit(0)

    # Step 3: Return hashes if no export
    return hashes
