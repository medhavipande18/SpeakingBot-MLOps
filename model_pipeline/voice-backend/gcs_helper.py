"""
Google Cloud Storage helper functions for RAG assistant.
"""
import os
import json
from google.cloud import storage

def download_blob_to_file(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket to a local file."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    
    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
    blob.download_to_filename(destination_file_name)
    
    print(f"Downloaded {source_blob_name} to {destination_file_name}")

def upload_blob_from_file(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(source_file_name)
    
    print(f"Uploaded {source_file_name} to {destination_blob_name}")

def check_if_blob_exists(bucket_name, blob_name):
    """Check if a blob exists in the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    return blob.exists()

def get_gcs_bucket_name():
    """Get the GCS bucket name from environment variables."""
    # First try the environment variable
    bucket_name = os.getenv('GCS_BUCKET')
    
    # If running in App Engine, check if there's a configured value
    if not bucket_name and os.getenv('USE_GCS') == 'true':
        bucket_name = os.getenv('GCS_BUCKET')
    
    return bucket_name

def ensure_index_files():
    """
    Ensures FAISS index files are available locally.
    If not present locally, attempts to download from GCS.
    """
    bucket_name = get_gcs_bucket_name()
    if not bucket_name:
        print("No GCS bucket configured. Using local files only.")
        return
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_dir, "faiss_index.index")
    metadata_path = os.path.join(base_dir, "index_metadata.json")
    
    # Check if local files exist
    local_index_exists = os.path.exists(index_path)
    local_metadata_exists = os.path.exists(metadata_path)
    
    # If both exist locally, nothing to do
    if local_index_exists and local_metadata_exists:
        print("Using existing local index files.")
        return
    
    # Check if files exist in GCS
    gcs_index_exists = check_if_blob_exists(bucket_name, "model/faiss_index.index")
    gcs_metadata_exists = check_if_blob_exists(bucket_name, "model/index_metadata.json")
    
    # Download from GCS if needed
    if not local_index_exists and gcs_index_exists:
        download_blob_to_file(bucket_name, "model/faiss_index.index", index_path)
    
    if not local_metadata_exists and gcs_metadata_exists:
        download_blob_to_file(bucket_name, "model/index_metadata.json", metadata_path)