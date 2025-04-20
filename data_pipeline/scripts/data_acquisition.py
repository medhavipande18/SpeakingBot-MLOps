import logging
import requests
import os
import gzip

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

def check_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")
    else:
        logging.info(f"Directory already exists: {directory}")

def download_file(url, file_path):
    try:
        response = requests.get(url, stream=True, verify=False)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
            logging.info(f"File downloaded successfully: {file_path}")
        else:
            logging.error(f"Failed to download {url}. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error downloading file from {url}: {e}")

def get_file_content(file_path):
    try:
        if file_path.endswith(".gz"):
            with gzip.open(file_path, "rt", encoding="utf-8") as file:
                logging.info(f"Reading first 5 lines of {file_path}")
                for _ in range(5):
                    line = file.readline().strip()
                    if not line:
                        break
                    logging.info(line)
        else:
            with open(file_path, "r", encoding="utf-8") as file:
                logging.info(f"Reading first 5 lines of {file_path}")
                for _ in range(5):
                    line = file.readline().strip()
                    if not line:
                        break
                    logging.info(line)
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")

if __name__ == "__main__":
    
    logging.info("Starting data acquisition...")
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, "data")
    check_directory_exists(data_dir)
    
    review_url = "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/Software.jsonl.gz"
    review_file = os.path.join(data_dir, "software_reviews.jsonl.gz")
    
    download_file(review_url, review_file)
    get_file_content(review_file)

    metadata_url = "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_Software.jsonl.gz"
    metadata_file = os.path.join(data_dir, "software_metadata.jsonl.gz")
    
    download_file(metadata_url, metadata_file)
    get_file_content(metadata_file)
    
    logging.info("Data acquisition completed successfully.")