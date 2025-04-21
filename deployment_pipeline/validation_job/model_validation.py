"""
Model validation script for RAG-based assistant.
"""
import os
import json
import faiss
import numpy as np
import openai
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
import random
from google.cloud import storage  # ✅ NEW

# Load env and API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
EMBED_MODEL = "text-embedding-3-small"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load GCS config
GCS_BUCKET = os.getenv("GCS_BUCKET")
GCS_PREFIX = os.getenv("GCS_PREFIX", "")

# Build paths
index_blob = f"{GCS_PREFIX}/faiss_index.index" if GCS_PREFIX else "faiss_index.index"
metadata_blob = f"{GCS_PREFIX}/index_metadata.json" if GCS_PREFIX else "index_metadata.json"

INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.index")
METADATA_PATH = os.path.join(BASE_DIR, "index_metadata.json")
VALIDATION_QUERIES_PATH = os.path.join(BASE_DIR, "data", "validation_queries.json")
VALIDATION_RESULTS_PATH = os.path.join(BASE_DIR, "validation_results.json")

# Validation thresholds
MIN_RECALL_THRESHOLD = 0.7
MIN_MRR_THRESHOLD = 0.6

# ✅ Helper to download from GCS
def download_from_gcs(bucket_name, blob_name, destination_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(destination_path)

def load_validation_queries():
    if os.path.exists(VALIDATION_QUERIES_PATH):
        with open(VALIDATION_QUERIES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        synthetic_queries = []
        for idx, item in enumerate(random.sample(metadata, min(20, len(metadata)))):
            title = item.get("title", "")
            if title:
                synthetic_queries.append({
                    "query": f"Tell me about {title}",
                    "expected_asin": item.get("parent_asin", ""),
                    "description": f"Query about product: {title}"
                })
        
        os.makedirs(os.path.dirname(VALIDATION_QUERIES_PATH), exist_ok=True)
        with open(VALIDATION_QUERIES_PATH, "w", encoding="utf-8") as f:
            json.dump(synthetic_queries, f, indent=2)
        
        return synthetic_queries

def get_query_embedding(text):
    response = openai.embeddings.create(
        input=[text],
        model=EMBED_MODEL
    )
    return np.array(response.data[0].embedding, dtype="float32")

def evaluate_rag_system():
    print("⏬ Downloading index and metadata from GCS...")
    download_from_gcs(GCS_BUCKET, index_blob, INDEX_PATH)
    download_from_gcs(GCS_BUCKET, metadata_blob, METADATA_PATH)

    print("📦 Loading FAISS index and metadata...")
    faiss_index = faiss.read_index(INDEX_PATH)

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)

    asin_to_index = {meta.get("parent_asin"): idx for idx, meta in enumerate(metadata_list) if meta.get("parent_asin")}

    validation_queries = load_validation_queries()

    total_queries = len(validation_queries)
    recall_at_k = {1: 0, 3: 0, 5: 0}
    mrr = 0
    results = []

    print(f"🔍 Evaluating model on {total_queries} validation queries...")

    for query_data in tqdm(validation_queries):
        query = query_data["query"]
        expected_asin = query_data["expected_asin"]

        query_vector = get_query_embedding(query).reshape(1, -1)
        D, I = faiss_index.search(query_vector, 5)

        retrieved_asins = []
        for idx in I[0]:
            if idx >= 0 and idx < len(metadata_list):
                retrieved_asins.append(metadata_list[idx]["parent_asin"])

        for k_val in recall_at_k:
            if expected_asin in retrieved_asins[:k_val]:
                recall_at_k[k_val] += 1

        if expected_asin in retrieved_asins:
            rank = retrieved_asins.index(expected_asin) + 1
            mrr += 1.0 / rank

        results.append({
            "query": query,
            "expected_asin": expected_asin,
            "retrieved_asins": retrieved_asins,
            "found_at_position": retrieved_asins.index(expected_asin) + 1 if expected_asin in retrieved_asins else -1
        })

    for k in recall_at_k:
        recall_at_k[k] = recall_at_k[k] / total_queries

    mrr = mrr / total_queries
    validation_pass = recall_at_k[3] >= MIN_RECALL_THRESHOLD and mrr >= MIN_MRR_THRESHOLD

    validation_results = {
        "total_queries": total_queries,
        "recall_at_1": recall_at_k[1],
        "recall_at_3": recall_at_k[3],
        "recall_at_5": recall_at_k[5],
        "mrr": mrr,
        "validation_pass": validation_pass,
        "detailed_results": results
    }

    with open(VALIDATION_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(validation_results, f, indent=2)

    print("✅ Validation Results:")
    print(f"Recall@1: {recall_at_k[1]:.4f}")
    print(f"Recall@3: {recall_at_k[3]:.4f}")
    print(f"Recall@5: {recall_at_k[5]:.4f}")
    print(f"MRR: {mrr:.4f}")
    print(f"Validation {'PASSED' if validation_pass else 'FAILED'}")

    return validation_results

if __name__ == "__main__":
    evaluate_rag_system()
