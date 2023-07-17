# Folder Synchronization Script

This Python script allows you to synchronize two folders, ensuring that the replica folder maintains an identical copy of the source folder. The synchronization is one-way, and it can be performed periodically based on the specified interval.

## Usage

```
python sync_script.py /path/to/source_folder /path/to/replica_folder interval /path/to/log_file.txt
```

- `/path/to/source_folder`: The path to the source folder that needs to be synchronized.
- `/path/to/replica_folder`: The path to the replica folder where an exact copy of the source folder will be maintained.
- `interval`: The synchronization interval in seconds. The script will perform synchronization at the specified time interval.
- `/path/to/log_file.txt`: The path to the log file where the synchronization operations will be logged.

## How It Works

The script uses the MD5 hash to compare files between the source and replica folders. Here's how it works:

1. The MD5 hash of each file in both the source and replica folders is calculated.
2. The script compares the list of files and their MD5 hashes between the source and replica folders.
3. Files that are missing or have different MD5 hashes in the replica folder will be copied from the source folder.
4. Files that exist in the replica folder but not in the source folder will be removed from the replica folder.

## Requirements

The script relies on the Python standard library and does not use any third-party libraries for folder synchronization.

## Analysis

Advantages:

- Hash functions, such as MD5, provide efficient detection of file changes, allowing quick determination of which files need to be copied or removed during synchronization.
- Calculating the hash takes a small amount of time, even for large files, and is independent of folder sizes or structure.

Disadvantages:

- Performing a full hash recalculation for each file during every synchronization may take more time than recursive comparison when changes are minimal.
- Copying all files anew may require more input-output (I/O) operations and consume more disk space, especially for large files.
