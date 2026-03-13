#!/usr/bin/env python3
"""
Deleted Files Recovery Challenge
Difficulty: Medium
Points: 80
Category: Digital Forensics

Description:
A user accidentally deleted an important file containing a flag.
Can you recover the deleted file from this disk image?

This script creates a disk image with deleted files for forensic analysis.
"""

import os
import tempfile
import subprocess
import shutil

def create_filesystem_image():
    """Create a filesystem image with deleted files"""
    image_file = "challenge_disk.img"
    mount_point = "/tmp/challenge_mount"

    # Create a disk image (10MB)
    subprocess.run(["dd", "if=/dev/zero", f"of={image_file}", "bs=1M", "count=10"], check=True)

    # Create filesystem
    subprocess.run(["mkfs.ext4", image_file], check=True)

    # Create mount point
    os.makedirs(mount_point, exist_ok=True)

    try:
        # Mount the image
        subprocess.run(["sudo", "mount", "-o", "loop", image_file, mount_point], check=True)

        # Create some normal files
        with open(f"{mount_point}/readme.txt", "w") as f:
            f.write("Welcome to the forensics challenge!\n")
            f.write("Some files have been deleted from this system.\n")
            f.write("Can you recover them?\n")

        with open(f"{mount_point}/notes.txt", "w") as f:
            f.write("Meeting notes:\n")
            f.write("- Discuss project timeline\n")
            f.write("- Review security protocols\n")
            f.write("- Plan next sprint\n")

        # Create the important file with flag
        flag_content = """CONFIDENTIAL DOCUMENT
=====================

Project: SecureVault Development
Date: 2024-01-15
Classification: TOP SECRET

The secret flag for this challenge is: flag{forensics_recovery_expert}

This information must not be disclosed to unauthorized personnel.

Additional security measures:
- All communications encrypted
- Access logs monitored
- Regular security audits

---
End of Document
"""

        with open(f"{mount_point}/secret_flag.txt", "w") as f:
            f.write(flag_content)

        # Create some decoy files
        with open(f"{mount_point}/config.ini", "w") as f:
            f.write("[settings]\n")
            f.write("debug=false\n")
            f.write("log_level=info\n")

        # Sync to ensure files are written
        subprocess.run(["sync"], check=True)

        # Delete the important file
        os.remove(f"{mount_point}/secret_flag.txt")

        # Sync again
        subprocess.run(["sync"], check=True)

        print("Files created and flag file deleted")

    finally:
        # Unmount
        subprocess.run(["sudo", "umount", mount_point], check=True)
        os.rmdir(mount_point)

    print(f"Disk image created: {image_file}")
    return image_file

def demonstrate_recovery():
    """Demonstrate file recovery techniques"""
    print("\n=== File Recovery Demonstration ===")
    print("To recover deleted files from the disk image, you can use:")
    print("1. testdisk - Powerful file recovery tool")
    print("2. photorec - Recover files by file signatures")
    print("3. extundelete - Ext filesystem undelete utility")
    print("4. sleuthkit - Digital forensics toolkit")
    print("5. strings - Extract readable strings from binary files")

    print("\nExample commands:")
    print("# Mount the image read-only")
    print("sudo mkdir /mnt/evidence")
    print("sudo mount -o ro,loop challenge_disk.img /mnt/evidence")

    print("\n# Use strings to find text data")
    print("strings challenge_disk.img | grep -i flag")

    print("\n# Use extundelete to recover deleted files")
    print("sudo extundelete challenge_disk.img --restore-all")

    print("\n# Use testdisk for recovery")
    print("sudo testdisk challenge_disk.img")

    print("\n# Use sleuthkit tools")
    print("fls challenge_disk.img")
    print("icat challenge_disk.img [inode_number]")

def create_solution_script():
    """Create a solution script"""
    solution_script = """#!/bin/bash
# Solution script for deleted files recovery challenge

echo "=== Deleted Files Recovery Solution ==="

# Method 1: Use strings to find the flag directly
echo "Method 1: Using strings command"
echo "strings challenge_disk.img | grep -A5 -B5 flag{"

# Method 2: Use testdisk/photorec
echo -e "\nMethod 2: Using photorec (interactive)"
echo "photorec challenge_disk.img"

# Method 3: Use extundelete
echo -e "\nMethod 3: Using extundelete"
echo "sudo extundelete challenge_disk.img --restore-all"

# Method 4: Manual analysis with hexdump
echo -e "\nMethod 4: Manual analysis with hexdump"
echo "hexdump -C challenge_disk.img | grep -i flag -A2 -B2"

echo -e "\nThe flag should be: flag{forensics_recovery_expert}"
"""

    with open("solution.sh", "w") as f:
        f.write(solution_script)
    os.chmod("solution.sh", 0o755)
    print("Solution script created: solution.sh")

if __name__ == "__main__":
    print("Creating deleted files recovery challenge...")

    try:
        image_file = create_filesystem_image()
        demonstrate_recovery()
        create_solution_script()

        print(f"\nChallenge created successfully!")
        print(f"Disk image: {image_file}")
        print(f"Hidden flag: flag{{forensics_recovery_expert}}")
        print("\nParticipants need to:")
        print("1. Analyze the disk image")
        print("2. Identify deleted files")
        print("3. Recover the deleted file containing the flag")
        print("4. Extract the flag from the recovered content")

    except subprocess.CalledProcessError as e:
        print(f"Error creating challenge: {e}")
        print("Note: This script requires root privileges for mounting filesystems")
        print("You can run it with: sudo python3 create_challenge.py")
    except Exception as e:
        print(f"Unexpected error: {e}")