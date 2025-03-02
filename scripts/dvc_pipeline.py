import logging
import os
import subprocess
import json
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

# Load configuration
CONFIG_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
if not os.path.exists(CONFIG_PATH):
    logging.error(f"Config file not found: {CONFIG_PATH}")
    raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")

with open(CONFIG_PATH, "r") as config_file:
    config = json.load(config_file)

service_account_path = os.path.join(PROJECT_DIR, "config", config["service_account_json"])
bucket_name = config["bucket_name"]
folder_path = os.path.join(PROJECT_DIR, "data")
files_to_track = config["files_to_upload"]

def run_command(command, working_dir=PROJECT_DIR):
    """Executes a shell command and logs the result."""
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=working_dir, capture_output=True, text=True)
        logging.info(f"Successfully executed: {' '.join(command)}\nOutput:\n{result.stdout}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running command: {' '.join(command)}\nError:\n{e.stderr}")
        exit(1)

# Initialize DVC if not already initialized
if not os.path.exists(os.path.join(PROJECT_DIR, ".dvc")):
    logging.info("Initializing DVC in the project root...")
    run_command(["dvc", "init", "--no-scm"])
else:
    logging.info("DVC is already initialized.")

# Enable auto-staging for DVC
logging.info("Enabling DVC auto-staging...")
run_command(["dvc", "config", "core.autostage", "true"])

# Add files to DVC
logging.info("Adding files to DVC tracking...")
for file in files_to_track:
    file_path = os.path.join(folder_path, file)
    if os.path.exists(file_path):
        run_command(["dvc", "add", file_path])
    else:
        logging.warning(f"File {file_path} not found, skipping.")

def get_gcs_file_id(bucket_name, filename):
    client = storage.Client.from_service_account_json(service_account_path)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    
    if blob.exists():
        logging.info(f"Retrieved file ID for {filename} from GCS: {blob.generation}")
        return str(blob.generation)
    else:
        logging.error(f"File {filename} not found in GCS bucket {bucket_name}")
        return None

# Generate version tags using GCS file IDs
file_version_tags = []
for file in files_to_track:
    file_id = get_gcs_file_id(bucket_name, file)
    if file_id:
        file_version_tags.append(f"{file}-{file_id}")

if not file_version_tags:
    logging.error("No valid file IDs retrieved from GCS. Aborting DVC commit.")
    exit(1)

version_tag = "_".join(file_version_tags)

# Commit DVC changes
logging.info("Committing DVC metadata to Git...")
run_command(["git", "add", "*.dvc", ".dvcignore", ".gitignore"])
run_command(["git", "commit", "-m", f"Track dataset versions with DVC - {version_tag}"])
run_command(["git", "tag", f"{version_tag}"])
run_command(["git", "push", "origin", "main", "--tags"])

logging.info(f"DVC pipeline execution complete. Version: {version_tag}")
