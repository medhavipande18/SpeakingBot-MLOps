import os
from dotenv import load_dotenv
load_dotenv()

# Source for latest processed metadata
METADATA_URL = "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_Software.jsonl.gz"
TEMP_LOCAL_FILE = "/tmp/latest_metadata.jsonl.gz"

# GCS reference
GCS_BUCKET_NAME = "speaking-chatbot-data"
GCS_BLOB_NAME = "software_metadata_preprocessed.jsonl"

# Slack settings
SLACK_WEBHOOK_URL = os.getenv("https://hooks.slack.com/services/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")

# Threshold
DRIFT_THRESHOLD = 0.2

# Output
DRIFT_REPORT_PATH = "deployment_pipeline/logs/drift_report.html"