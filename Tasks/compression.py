import os
import zipfile
import tarfile
from db.mongodb import get_db
import time
import logging

# Create a logger for compression
logger = logging.getLogger('compression')
logger.setLevel(logging.DEBUG)

# Create file handler which logs even debug messages
fh = logging.FileHandler('../logs/compression.log')
fh.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)

# Suppress pymongo logs
logging.getLogger('pymongo').setLevel(logging.CRITICAL)

# MongoDB connection
db = get_db('Automation')
collection = db['compression_logs']

def log_compression(compressed_filename, compression_format, original_size, compressed_size):
    log_entry = {
        "compressed_filename": os.path.basename(compressed_filename),
        "compression_format": compression_format,
        "original_size_MB": original_size,
        "compressed_size_MB": compressed_size,
        "compressed_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
    try:
        result = collection.insert_one(log_entry)
        logger.debug(f"Logged compression to MongoDB: {log_entry}, Inserted ID: {result.inserted_id}")
        print(f"Logged compression to MongoDB: {log_entry}, Inserted ID: {result.inserted_id}")
    except Exception as e:
        logger.error(f"Error logging compression to MongoDB: {str(e)}")
        print(f"Error logging compression to MongoDB: {str(e)}")

def compress_files(directory, compressed_file_name, single_file=None, format='zip', delete_original=False):
    """Compress files in a given directory into ZIP or TAR format"""
    if not os.path.isdir(directory):
        logger.error(f"❌ Error: {directory} is not a valid directory.")
        print(f"❌ Error: {directory} is not a valid directory.")
        return

    if single_file:
        files_to_compress = [os.path.join(directory, single_file)]
    else:
        files_to_compress = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    compressed_filename = os.path.join(directory, f"{compressed_file_name}.{format}")

    try:
        if format == 'zip':
            with zipfile.ZipFile(compressed_filename, 'w') as zipf:
                for file in files_to_compress:
                    zipf.write(file, os.path.basename(file))
        elif format == 'tar':
            with tarfile.open(compressed_filename, 'w:gz') as tarf:
                for file in files_to_compress:
                    tarf.add(file, arcname=os.path.basename(file))
        else:
            logger.error("❌ Unsupported format! Use 'zip' or 'tar'.")
            print("❌ Unsupported format! Use 'zip' or 'tar'.")
            return

        # Calculate total original size
        total_original_size = sum(os.path.getsize(file) for file in files_to_compress) / (1024 * 1024)  # MB
        compressed_size = os.path.getsize(compressed_filename) / (1024 * 1024)  # MB

        # Log the compression details
        log_compression(compressed_filename, format, total_original_size, compressed_size)

        # Delete original files if required
        if delete_original:
            for file in files_to_compress:
                os.remove(file)

        logger.info(f"✅ Files compressed into: {compressed_filename}")
        print(f"✅ Files compressed into: {compressed_filename}")

    except Exception as e:
        logger.error(f"❌ Error during compression: {e}")
        print(f"❌ Error during compression: {e}")

def run_compression():
    directory = input("📁 Enter directory: ").strip()
    compressed_file_name = input("📦 Compressed file name: ").strip()
    single_file = input("📄 File to compress (leave blank for all): ").strip()
    format = input("🔄 Format (zip/tar): ").strip().lower()
    delete_original = input("❌ Delete originals? (yes/no): ").strip().lower() == 'yes'

    compress_files(directory, compressed_file_name, single_file if single_file else None, format, delete_original)

if __name__ == "__main__":
    run_compression()