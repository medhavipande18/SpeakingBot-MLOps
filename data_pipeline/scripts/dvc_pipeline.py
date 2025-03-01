import os
import subprocess
import json
import logging
from google.cloud import storage

# Paths
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(PROJECT_DIR, "config", "config.json")
LOG_FILE = os.path.join(PROJECT_DIR, "logs", "pipeline.log")
DATA_DIR = os.path.join(PROJECT_DIR, "data")

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        logging.error(f"Missing config file at {CONFIG_PATH}")
        raise FileNotFoundError(CONFIG_PATH)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def run_command(command, cwd=PROJECT_DIR):
    try:
        result = subprocess.run(
            command, cwd=cwd, check=True,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        logging.info(f"Executed: {' '.join(command)}\n{result.stdout}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed: {' '.join(command)}\n{e.stderr}")
        raise

def initialize_dvc():
    dvc_dir = os.path.join(PROJECT_DIR, ".dvc")
    if not os.path.exists(dvc_dir):
        logging.info("Initializing DVC...")
        run_command([r"C:\Users\Hp\AppData\Roaming\Python\Python312\Scripts\dvc.exe", "init"])
    else:
        logging.info("DVC already initialized.")
    run_command(["DVC_PATH", "config", "core.autostage", "true"])

def add_files_to_dvc(files):
    for file in files:
        file_path = os.path.join(DATA_DIR, file)
        if os.path.exists(file_path):
            run_command(["DVC_PATH", "add", file_path])
        else:
            logging.warning(f"Skipping missing file: {file_path}")

def get_gcs_file_id(bucket_name, filename, service_account_path):
    try:
        client = storage.Client.from_service_account_json(service_account_path)
        blob = client.bucket(bucket_name).blob(filename)
        if blob.exists():
            logging.info(f"{filename} GCS generation: {blob.generation}")
            return str(blob.generation)
        else:
            logging.warning(f"{filename} not found in bucket {bucket_name}")
            return None
    except Exception as e:
        logging.error(f"GCS error for {filename}: {e}")
        return None

def commit_and_tag_version(file_tags):
    run_command(["git", "add", "*.dvc", ".dvcignore", ".gitignore"])
    version_tag = "_".join(file_tags)
    commit_msg = f"Track dataset versions with DVC - {version_tag}"
    run_command(["git", "commit", "-m", commit_msg])
    run_command(["git", "tag", version_tag])
    run_command(["git", "push", "origin", "main", "--tags"])
    logging.info(f"Committed DVC changes with tag: {version_tag}")
    return version_tag

def main():
    config = load_config()
    files_to_track = config.get("files_to_upload", [])
    bucket_name = config["bucket_name"]
    service_account_path = os.path.join(PROJECT_DIR, "config", config["service_account_json"])

    initialize_dvc()
    add_files_to_dvc(files_to_track)

    file_tags = []
    for file in files_to_track:
        file_id = get_gcs_file_id(bucket_name, file, service_account_path)
        if file_id:
            file_tags.append(f"{file}-{file_id}")

    if not file_tags:
        logging.error("No GCS file versions found. DVC commit aborted.")
        return

    version = commit_and_tag_version(file_tags)
    logging.info(f"Data versioning complete. Version: {version}")

if __name__ == "__main__":
    main()