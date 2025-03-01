import json
import os
import gzip
import logging
import requests


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


SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def send_slack_alert(message):

    payload = {"text": f":warning: *Data Anomaly Detected* :warning:\n{message}"}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            logging.info("Slack alert sent successfully")
        else:
            logging.error(f"Failed to send Slack alert: {response.text}")
    except Exception as e:
        logging.error(f"Error sending Slack alert: {e}")


def detect_anomalies(record):
    """Detects anomalies such as missing values, outliers, and invalid formats."""
    print("Inside anamolies")
    anomalies = []

    # Check for missing values
    for key, value in record.items():
        if value in [None, "", "N/A", "Unknown"]:
            anomalies.append(f"Missing value detected in `{key}`")

    # Check for outliers (e.g., negative price)
    if "price" in record and isinstance(record["price"], (int, float)) and record["price"] < 0:
        anomalies.append(f"Outlier detected: Negative price `{record['price']}`")

    # Check for invalid formats (e.g., rating should be between 1 and 5)
    if "overall" in record and isinstance(record["overall"], (int, float)) and not (1 <= record["overall"] <= 5):
        anomalies.append(f"Invalid rating detected: `{record['overall']}`")

    if anomalies:
        message = "\n".join(anomalies)
        logging.warning(message)
        send_slack_alert(message)

    return record


def clean_data(record):
    """Cleans the data by handling missing values and normalizing strings."""
    cleaned_record = {}
    for key, value in record.items():
        if isinstance(value, str):
            cleaned_value = value.strip() if value.strip() else "Unknown"
            cleaned_record[key] = cleaned_value

        elif isinstance(value, (int, float)):
            cleaned_record[key] = value

        elif isinstance(value, bool):
            cleaned_record[key] = bool(value)

        elif value is None:
            cleaned_record[key] = "N/A"

        elif isinstance(value, list):
            cleaned_record[key] = [clean_data(item) if isinstance(item, dict) else item.strip() if isinstance(item, str) else "N/A" if item is None else item for item in value]

        elif isinstance(value, dict):
            cleaned_record[key] = clean_data(value)

        else:
            cleaned_record[key] = str(value)

    return cleaned_record


def transform_data(record):

    transformed_record = {}
    for key, value in record.items():
        new_key = key.lower().replace(" ", "_")  # Standardizing column names

        # Recursively transform nested dictionaries
        if isinstance(value, dict):
            transformed_record[new_key] = transform_data(value)
        else:
            transformed_record[new_key] = value
    
    return transformed_record


def feature_engineering(record):

    if "price" in record and isinstance(record["price"], (int, float)):
        if record["price"] < 100:
            record["price_category"] = "Low"
        elif 100 <= record["price"] <= 200:
            record["price_category"] = "Medium"
        else:
            record["price_category"] = "High"

    if "overall" in record and isinstance(record["overall"], (int, float)):
        if record["overall"] >= 4.0:
            record["review_sentiment"] = "Positive"
        elif 2.5 <= record["overall"] < 4.0:
            record["review_sentiment"] = "Neutral"
        else:
            record["review_sentiment"] = "Negative"
    
    return record


def preprocess_record(record):
    record = clean_data(record)
    record = transform_data(record)
    record = feature_engineering(record)
    return record


def preprocess_jsonl_file(input_file, output_file):
    """Processes a JSONL.GZ file and saves the output as a JSONL file after transformations."""
    if not os.path.exists(input_file):
        logging.info(f"File not found: {input_file}")
        return
    
    # Detect if the input file is gzip compressed
    with open(input_file, "rb") as test_f:
        is_gzip = test_f.read(2) == b'\x1f\x8b'  # Check for Gzip signature

    # Open the file correctly based on compression type
    open_func = gzip.open if is_gzip else open

    with open_func(input_file, "rt", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            try:
                record = json.loads(line)
                processed_record = preprocess_record(record)
                outfile.write(json.dumps(processed_record) + "\n")
            except json.JSONDecodeError as e:
                logging.info(f"Skipping invalid JSON line: {e}")

    logging.info(f"Preprocessed data saved to: {output_file}")


def get_file_content(file_path, num_lines=5):
    """Reads and prints a few lines from a processed file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for _ in range(num_lines):
                line = file.readline().strip()
                if not line:
                    break
                logging.info(line)
    except Exception as e:
        logging.info(f"Error reading file {file_path}: {e}")


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, "data")

    # Input file (compressed .jsonl.gz)
    metadata_file = os.path.join(data_dir, "software_metadata.jsonl.gz")
    
    # Output file (uncompressed .jsonl)
    cleaned_metadata_file = os.path.join(data_dir, "software_metadata_preprocessed.jsonl")

    preprocess_jsonl_file(metadata_file, cleaned_metadata_file)
    get_file_content(cleaned_metadata_file)

    # Input file (compressed .jsonl.gz)
    reviews_file = os.path.join(data_dir, "software_reviews.jsonl.gz")
    
    # Output file (uncompressed .jsonl)
    cleaned_reviews_file = os.path.join(data_dir, "software_reviews_preprocessed.jsonl")

    preprocess_jsonl_file(reviews_file, cleaned_reviews_file)
    get_file_content(cleaned_reviews_file)
