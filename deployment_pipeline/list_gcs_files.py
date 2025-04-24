# deployment_pipeline/list_gcs_files.py

from google.cloud import storage
import os

# Set your project ID if needed
bucket_name = "speaking-chatbot-data"

def list_blobs(bucket_name):
    client = storage.Client()
    blobs = client.list_blobs(bucket_name)

    print(f"📁 Files in bucket '{bucket_name}':")
    for blob in blobs:
        print(f" - {blob.name}")

if __name__ == "__main__":
    os.environ["GCP_SA_KEY"] = "credentials/mlops-speakingchatbot-bb5b1137c62b.json"
    list_blobs(bucket_name)