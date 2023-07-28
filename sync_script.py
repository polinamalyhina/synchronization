import os
import hashlib
import argparse
import time
import logging
from typing import Any


def log_action(action: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                logging.info(f"Success with {action} operation")
                return result
            except Exception as e:
                logging.error(f"Error while {action} operation: {e}")
                raise e

        return wrapper

    return decorator


def make_set(folder):
    folder_files_set = set(
        os.path.relpath(os.path.join(root, file), folder) for root, _, files in
        os.walk(folder) for file in files)
    return folder_files_set


def calculate_md5(filepath: str) -> str:
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def copy_file_by_chunks(source_path: str, replica_path: str) -> None:
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


@log_action("COPY_Files")
def copy_files(source, replica):
    source_files_set = make_set(source)
    replica_files_set = make_set(replica)

    for file in source_files_set - replica_files_set:
        source_path = os.path.join(source, file)
        replica_path = os.path.join(replica, file)

        copy_file_by_chunks(source_path, replica_path)


@log_action("COPY_Dirs")
def copy_dirs(source, replica):
    for root, dirs, _ in os.walk(source):
        for d in dirs:
            source_dir = os.path.join(root, d)
            replica_dir = os.path.join(replica, os.path.relpath(source_dir, source))
            if not os.path.exists(replica_dir):
                os.makedirs(replica_dir)


@log_action("REMOVE_Files")
def remove_files(source, replica):
    source_files_set = make_set(source)
    replica_files_set = make_set(replica)

    for file in replica_files_set - source_files_set:
        replica_path = os.path.join(replica, file)

        os.remove(replica_path)


@log_action("REMOVE_Dirs")
def remove_dirs(source, replica):
    for root, dirs, _ in os.walk(replica, topdown=False):
        for d in dirs:
            replica_dir = os.path.join(root, d)
            source_dir = os.path.join(source, os.path.relpath(replica_dir, replica))
            if not os.path.exists(source_dir):
                remove_directory_recursive(replica_dir)


@log_action("UPDATE_Files")
def update_files(source, replica):
    source_files_set = make_set(source)
    replica_files_set = make_set(replica)

    for file in source_files_set & replica_files_set:
        source_path = os.path.join(source, file)
        replica_path = os.path.join(replica, file)

        if os.path.isfile(source_path) and os.path.isfile(replica_path):
            source_md5 = calculate_md5(source_path)
            replica_md5 = calculate_md5(replica_path)

            if source_md5 != replica_md5:
                os.remove(replica_path)
                copy_file_by_chunks(source_path, replica_path)


def synchronize_folders(source: str, replica: str, log_file: Any) -> None:
    copy_files(source, replica)
    remove_files(source, replica)
    update_files(source, replica)
    copy_dirs(source, replica)
    remove_dirs(source, replica)
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
