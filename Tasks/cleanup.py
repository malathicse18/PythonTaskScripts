import os
import time
import shutil
import logging
from pymongo import MongoClient
from db.mongodb import get_db

# Setup logging
logging.basicConfig(filename='../logs/cleanup.log', level=logging.DEBUG)

# Suppress pymongo logs
logging.getLogger('pymongo').setLevel(logging.CRITICAL)

# MongoDB connection
db = get_db('Automation')
collection = db['deletion_logs']

def delete_files(directory, age=None, size=None, file_type=None, archive=False):
    logging.debug(f"Starting delete_files with directory={directory}, age={age}, size={size}, file_type={file_type}, archive={archive}")
    now = time.time()
    archive_dir = os.path.join(directory, 'archive')
    if archive and not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        logging.debug(f"Created archive directory at {archive_dir}")

    files_deleted = False

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        logging.debug(f"Checking file: {filename}")
        print(f"Checking file: {filename}")  # Print to console for immediate feedback
        if os.path.isfile(file_path):
            file_stat = os.stat(file_path)
            if age and (now - file_stat.st_mtime) > age * 86400:
                logging.debug(f"File {filename} is older than {age} days")
                print(f"File {filename} is older than {age} days")  # Print to console for immediate feedback
                handle_file(file_path, archive_dir, "File older than {} days".format(age), archive)
                files_deleted = True
            elif size and (file_stat.st_size > size * 1024 * 1024):
                logging.debug(f"File {filename} is larger than {size} MB")
                print(f"File {filename} is larger than {size} MB")  # Print to console for immediate feedback
                handle_file(file_path, archive_dir, "File larger than {} MB".format(size), archive)
                files_deleted = True
            elif file_type and filename.endswith(file_type):
                logging.debug(f"File {filename} is of type {file_type}")
                print(f"File {filename} is of type {file_type}")  # Print to console for immediate feedback
                handle_file(file_path, archive_dir, "File type {}".format(file_type), archive)
                files_deleted = True
            else:
                logging.debug(f"File {filename} does not meet any criteria")
                print(f"File {filename} does not meet any criteria")  # Print to console for immediate feedback

    if not files_deleted:
        print("No files met the specified criteria.")
        logging.debug("No files met the specified criteria.")

def handle_file(file_path, archive_dir, reason, archive):
    try:
        filename = os.path.basename(file_path)
        log_deletion(file_path, reason)  # Log the deletion before removing the file
        if archive:
            shutil.move(file_path, archive_dir)
            logging.info(f"Archived {filename} to {archive_dir}")
            print(f"Archived {filename} to {archive_dir}")  # Print to console for immediate feedback
        else:
            os.remove(file_path)
            logging.info(f"Deleted {filename}: {reason}")
            print(f"Deleted {filename}: {reason}")  # Print to console for immediate feedback
    except PermissionError:
        logging.error(f"Permission denied: {file_path}")
        print(f"Permission denied: {file_path}")  # Print to console for immediate feedback
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        # Removed the print statement for "File not found" to avoid showing it after deletion
    except Exception as e:
        logging.error(f"Error deleting {file_path}: {str(e)}")
        print(f"Error deleting {filename}: {str(e)}")  # Print to console for immediate feedback

def log_deletion(file_path, reason):
    log_entry = {
        "filename": os.path.basename(file_path),
        "filepath": file_path,
        "deleted_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "reason": reason,
        "size_MB": os.path.getsize(file_path) / (1024 * 1024)
    }
    try:
        # Ensure the database and collection are created
        db.command("ping")
        if 'deletion_logs' not in db.list_collection_names():
            db.create_collection('deletion_logs')
            print("Collection 'deletion_logs' created successfully.")
        result = collection.insert_one(log_entry)
        # print(f"Logged deletion to MongoDB: {log_entry}, Inserted ID: {result.inserted_id}")
        logging.debug(f"Logged deletion to MongoDB: {log_entry}")
    except Exception as e:
        print(f"Error logging deletion to MongoDB: {str(e)}")
        logging.error(f"Error logging deletion to MongoDB: {str(e)}")

def run_cleanup():
    directory = input("Enter the directory path: ")
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        print("No files found in the directory.")
        return
    else:
        print("Files found in the directory:")
        for file in files:
            print(file)

    print("Choose cleanup criteria:")
    print("1. Age")
    print("2. Size")
    print("3. File Type")
    criteria_choice = input("Enter your choice (1-3): ")

    age = size = file_type = None

    if criteria_choice == '1':
        age = int(input("Enter the age in days to delete files older than: "))
    elif criteria_choice == '2':
        size = int(input("Enter the size in MB to delete files larger than: "))
    elif criteria_choice == '3':
        file_type = input("Enter the file type to delete (e.g., .log, .tmp): ")
    else:
        print("Invalid choice. Please try again.")
        return

    archive = input("Move files to archive before deletion? (yes/no): ").lower() == 'yes'
    delete_files(directory, age, size, file_type, archive)

# Example usage
if __name__ == "__main__":
    run_cleanup()