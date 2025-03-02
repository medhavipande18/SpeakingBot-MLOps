import logging
import json
import os
from google.cloud import storage

# Ensure logs directory exists
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
logs_dir = os.path.join(PROJECT_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file_path = os.path.join(logs_dir, "pipeline.log")

# Configure logging
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Get project root directory
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(PROJECT_DIR, "config", "config.json")

# Load configuration
if not os.path.exists(CONFIG_PATH):
    logging.error(f"Config file not found: {CONFIG_PATH}")
    raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")

with open(CONFIG_PATH, "r") as config_file:
    config = json.load(config_file)

# Extract configuration
service_account_path = os.path.join(PROJECT_DIR, "config", config["service_account_json"])
bucket_name = config["bucket_name"]
folder_path = os.path.join(PROJECT_DIR, "data")
files_to_upload = config["files_to_upload"]

def upload_to_gcs(bucket_name, folder_path, filenames, service_account_path):
    """Uploads specified files to GCS and logs the unique IDs."""
    logging.info(f"Starting upload to GCS bucket: {bucket_name}")
    client = storage.Client.from_service_account_json(service_account_path)
    bucket = client.bucket(bucket_name)
    file_ids = {}

    for filename in filenames:
        file_path = os.path.join(folder_path, filename)
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            continue

        blob = bucket.blob(filename)
        blob.upload_from_filename(file_path)
        file_ids[filename] = blob.generation
        logging.info(f"Uploaded {filename} to GCS with ID {blob.generation}")

    return file_ids

if __name__ == "__main__":
    logging.info("Starting GCS upload script...")
    unique_ids = upload_to_gcs(bucket_name, folder_path, files_to_upload, service_account_path)
    logging.info(f"Uploaded File IDs: {unique_ids}")
    logging.info("GCS upload completed successfully.")