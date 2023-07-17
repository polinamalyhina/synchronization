import os
import hashlib
import argparse
import time
from typing import Dict, Any


def calculate_md5(filepath: str) -> str:
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_files_md5(folder_path: str) -> Dict[str, str]:
    files_md5 = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder_path)
            files_md5[relative_path] = calculate_md5(file_path)
    return files_md5


def copy_file(source_path: str, replica_path: str) -> None:
    replica_dir = os.path.dirname(replica_path)
    if not os.path.exists(replica_dir):
        os.makedirs(replica_dir)

    with open(source_path, 'rb') as src_file, open(replica_path, 'wb') as dest_file:
        dest_file.write(src_file.read())


def synchronize_folders(source: str, replica: str, log_file: Any) -> None:
    if not os.path.exists(replica):
        os.makedirs(replica)

    source_files = get_files_md5(source)
    replica_files = get_files_md5(replica)

    for rel_path, md5_hash in source_files.items():
        source_file = os.path.join(source, rel_path)
        replica_file = os.path.join(replica, rel_path)

        if rel_path in replica_files and md5_hash == replica_files[rel_path]:
            continue

        copy_file(source_file, replica_file)

        log_entry = f"Copied: {source_file} -> {replica_file}\n"
        log_file.write(log_entry)
        print(log_entry.strip())

    for rel_path in set(replica_files) - set(source_files):
        replica_file = os.path.join(replica, rel_path)
        if os.path.exists(replica_file):
            os.remove(replica_file)
            log_entry = f"Removed: {replica_file}\n"
            log_file.write(log_entry)
            print(log_entry.strip())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("source", help="Source folder path")
    parser.add_argument("replica", help="Replica folder path")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")
    args = parser.parse_args()

    while True:
        with open(args.log_file, "a") as log_file:
            synchronize_folders(args.source, args.replica, log_file)
            log_file.write(f"--- Synchronization at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")

        time.sleep(args.interval)
