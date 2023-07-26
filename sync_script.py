
import os
import hashlib
import argparse
import time
import logging
from typing import Dict, Any


def calculate_md5(filepath: str) -> str:
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def copy_file(source_path: str, replica_path: str) -> None:
    replica_dir = os.path.dirname(replica_path)
    if not os.path.exists(replica_dir):
        os.makedirs(replica_dir)

    with open(source_path, 'rb') as src_file, open(replica_path, 'wb') as dest_file:
        for chunk in iter(lambda: src_file.read(4096), b""):
            dest_file.write(chunk)


def remove_directory_recursive(directory_path: str) -> None:
    for root, dirs, files in os.walk(directory_path, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for d in dirs:
            try:
                remove_directory_recursive(os.path.join(root, d))
                os.rmdir(os.path.join(root, d))
            except Exception as e:
                logging.error(f"Error while removing directory: {e}")
    os.rmdir(directory_path)


def synchronize_folders(source: str, replica: str, log_file: Any) -> None:
    source_files_set = set(os.path.relpath(os.path.join(root, file), source) for root, _, files in os.walk(source) for file in files)
    replica_files_set = set(os.path.relpath(os.path.join(root, file), replica) for root, _, files in os.walk(replica) for file in files)

    
    for file in source_files_set - replica_files_set:
        source_path = os.path.join(source, file)
        replica_path = os.path.join(replica, file)

        try:
            copy_file(source_path, replica_path)
            logging.info(f"Copied: {source_path} -> {replica_path}")
        except Exception as e:
            logging.error(f"Error while copying {source_path}: {e}")


    
    for file in replica_files_set - source_files_set:
        replica_path = os.path.join(replica, file)

        try:
            os.remove(replica_path)
            logging.info(f"Removed: {replica_path}")
        except Exception as e:
            logging.error(f"Error while removing {replica_path}: {e}")



    for file in source_files_set & replica_files_set:
        source_path = os.path.join(source, file)
        replica_path = os.path.join(replica, file)

        if os.path.isfile(source_path) and os.path.isfile(replica_path):
            source_md5 = calculate_md5(source_path)
            replica_md5 = calculate_md5(replica_path)

            if source_md5 != replica_md5:
                try:
                    os.remove(replica_path)
                    copy_file(source_path, replica_path)
                    logging.info(f"Updated: {source_path} -> {replica_path}")
                except Exception as e:
                    logging.error(f"Error while updating {replica_path}: {e}")

    
    for root, dirs, _ in os.walk(source):
        for d in dirs:
            source_dir = os.path.join(root, d)
            replica_dir = os.path.join(replica, os.path.relpath(source_dir, source))
            if not os.path.exists(replica_dir):
                try:
                    os.makedirs(replica_dir)
                    logging.info(f"Created directory: {replica_dir}")
                except Exception as e:
                    logging.error(f"Error while creating directory {replica_dir}: {e}")


    for root, dirs, _ in os.walk(replica, topdown=False):
        for d in dirs:
            replica_dir = os.path.join(root, d)
            source_dir = os.path.join(source, os.path.relpath(replica_dir, replica))
            if not os.path.exists(source_dir):
                try:
                    remove_directory_recursive(replica_dir)
                    logging.info(f"Removed directory: {replica_dir}")
                except Exception as e:
                    logging.error(f"Error while removing directory {replica_dir}: {e}")


    logging.info(f"--- Synchronization at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("source", help="Source folder path")
    parser.add_argument("replica", help="Replica folder path")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")
    args = parser.parse_args()

    logging.basicConfig(filename=args.log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

    while True:
        with open(args.log_file, "a", encoding="utf-8") as log_file:
            synchronize_folders(args.source, args.replica, log_file)
        time.sleep(args.interval)
