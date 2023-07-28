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

1. The script compares the list of files between the source and replica folders.
2. The MD5 hash of same files in both the source and replica folders is calculated.
3. Files and dirs that are missing or have different MD5 hashes in the replica folder will be copied from the source folder.
4. Files and dirs that exist in the replica folder but not in the source folder will be removed from the replica folder.

## Requirements

The script relies on the Python standard library and does not use any third-party libraries for folder synchronization.

## Updates

- Updated the copying algorithm to improve performance. Files are now copied in parts for faster and more efficient copying process.
- Improved the synchronization algorithm. Now, extra and unnecessary files are simply copied and deleted without the need to calculate hashes, reducing unnecessary overhead.
- Added handling for empty directories to ensure complete synchronization of directory structures.
- Revamped the logging system. Logging is now performed using a standard function and has been formatted as a decorator for better readability and maintainability.
- Conducted code refactoring to enhance code quality and readability.
