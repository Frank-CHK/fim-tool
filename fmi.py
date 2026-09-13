import os
import hashlib
import json
from datetime import datetime, timezone
import argparse

#hashh a single file using HASH256

def hash_file(file_path, algorithm="sha256"):
    hash_object = hashlib.new(algorithm)
    with open(file_path, "rb") as file_handle:
        while True:
            byte_chunk = file_handle.read(8192)
            if byte_chunk == b"":
                break
            hash_object.update(byte_chunk)
    return hash_object.hexdigest()

#Parse target directory and hash everything

def scan_directory(target_directory):
    file_hashes = {}
    for current_folder, _, file_names in os.walk(target_directory):
        for file_name in file_names:
            full_path = os.path.join(current_folder, file_name)
            try:
                file_hashes[full_path] = hash_file(full_path)
            except (PermissionError, FileNotFoundError, OSError) as error:
                print(f"Skipping {full_path}: {error}")
    return file_hashes

#Save data to disk

def save_baseline(file_hashes, target_directory, baseline_file_path = "baseline.json"):
    baseline_data = {
        "target_directory": os.path.abspath(target_directory),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": file_hashes,
    }
    with open(baseline_file_path, "w") as baseline_file:
        json.dump(baseline_data, baseline_file, indent=2)

#Load data from disk

def load_baseline(base_file_path="baseline.json"):
    if not os.path.exists(base_file_path): #check for existing baseline
        print(f"No baseline found at {base_file_path}. Create baseline first")
        return None
    with open(base_file_path, "r") as baseline_file:
        return json.load(baseline_file)

#Compare the data

def compare_snapshots(old_file_hashes, new_file_hashes):
    old_file_paths = set(old_file_hashes.keys())
    new_file_paths = set(new_file_hashes.keys())

    added_files = sorted(new_file_paths - old_file_paths)
    removed_files = sorted(old_file_paths - new_file_paths)
    modified_hashes = [
        file_path for file_path in sorted(old_file_paths & new_file_paths)
        if old_file_hashes[file_path] != new_file_hashes[file_path]
    ]

    return {
        "added": added_files,
        "removed": removed_files,
        "modified": modified_hashes,
    }

#Baseline command

def run_baseline(target_directory, baseline_file_path="baseline.json"):
    file_hashes = scan_directory(target_directory)
    save_baseline(file_hashes, target_directory, baseline_file_path)
    print(f"Baseline saved: {len(file_hashes)} files tracked.")

#Check command

def run_check(target_directory, baseline_file_path="baseline.json"):
    baseline_data = load_baseline(baseline_file_path)
    if baseline_data is None:
        return

    old_file_hashes = baseline_data["files"]
    new_file_hashes = scan_directory(target_directory)
    differences = compare_snapshots(old_file_hashes, new_file_hashes)

    total_changes = (
        len(differences["added"])
        + len(differences["removed"])
        + len(differences["modified"])
    )

    if total_changes == 0:
        print("No changed detected.")
        return

    print(f"{total_changes} change(s) detected:")
    for file_path in differences["added"]:
        print(f" + added:   {file_path}")
    for file_path in differences["removed"]:
        print(f" - removed: {file_path}")
    for file_path in differences["modified"]:
        print(f" * modified:    {file_path}")

# CLI

def main():
    parser = argparse.ArgumentParser(description="FMI tool")
    subcommands = parser.add_subparsers(dest="command", required=True)

    baseline_parser = subcommands.add_parser("baseline")
    baseline_parser.add_argument("directory")

    check_parser = subcommands.add_parser("check")
    check_parser.add_argument("directory")

    parsed_args = parser.parse_args()

    if parsed_args.command == "baseline":
        run_baseline(parsed_args.directory)
    elif parsed_args.command == "check":
        run_check(parsed_args.directory)

if __name__ == "__main__":
    main()