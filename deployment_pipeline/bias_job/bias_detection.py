"""
Bias detection script for RAG-based assistant.
"""
import os
import json
import faiss
import numpy as np
import openai
from dotenv import load_dotenv
from tqdm import tqdm
from collections import defaultdict
import pandas as pd
from google.cloud import storage  # <-- NEW

# Load env and API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
EMBED_MODEL = "text-embedding-3-small"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Get GCS vars
GCS_BUCKET = os.getenv("GCS_BUCKET")
GCS_PREFIX = os.getenv("GCS_PREFIX", "")

# Compose blob paths
index_blob = f"{GCS_PREFIX}/faiss_index.index" if GCS_PREFIX else "faiss_index.index"
metadata_blob = f"{GCS_PREFIX}/index_metadata.json" if GCS_PREFIX else "index_metadata.json"

# Local paths
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.index")
METADATA_PATH = os.path.join(BASE_DIR, "index_metadata.json")
BIAS_RESULTS_PATH = os.path.join(BASE_DIR, "bias_results.json")

# Download helper
def download_from_gcs(bucket_name, blob_name, destination_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(destination_path)

# Bias detection thresholds
MAX_PRICE_DISPARITY = 0.3
MIN_CATEGORY_REPRESENTATION = 0.1
MAX_RATING_BIAS = 0.2

def get_query_embedding(text):
    response = openai.embeddings.create(
        input=[text],
        model=EMBED_MODEL
    )
    return np.array(response.data[0].embedding, dtype="float32")

def detect_bias():
    print("⏬ Downloading index and metadata from GCS...")
    download_from_gcs(GCS_BUCKET, index_blob, INDEX_PATH)
    download_from_gcs(GCS_BUCKET, metadata_blob, METADATA_PATH)

    print("📦 Loading FAISS index and metadata...")
    faiss_index = faiss.read_index(INDEX_PATH)

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)

    test_queries = [
        "recommend software for beginners",
        "best rated software products",
        "affordable software options",
        "premium software solutions",
        "business software solutions",
        "graphic design software",
        "educational software",
        "productivity tools",
        "coding and development software",
        "cheap software options",
        "expensive professional software",
        "mid-range software products",
        "top-rated software",
        "popular software products",
        "highest rated software",
    ]

    price_tiers = defaultdict(int)
    categories = defaultdict(int)
    ratings = defaultdict(int)
    total_results = 0

    print("🔍 Running bias detection tests...")
    for query in tqdm(test_queries):
        query_vector = get_query_embedding(query).reshape(1, -1)
        D, I = faiss_index.search(query_vector, 5)

        for idx in I[0]:
            if idx >= 0 and idx < len(metadata_list):
                meta = metadata_list[idx]
                total_results += 1

                # Price
                price = meta.get("price", "")
                if isinstance(price, str) and price.startswith("$"):
                    try:
                        price_val = float(price.replace("$", "").replace(",", ""))
                        if price_val < 20:
                            price_tiers["low"] += 1
                        elif price_val < 100:
                            price_tiers["medium"] += 1
                        else:
                            price_tiers["high"] += 1
                    except:
                        pass

                # Category
                for category in meta.get("categories", []):
                    categories[category] += 1

                # Rating
                rating = meta.get("average_rating", "")
                if isinstance(rating, (int, float)):
                    if rating < 3:
                        ratings["low"] += 1
                    elif rating < 4:
                        ratings["medium"] += 1
                    else:
                        ratings["high"] += 1

    # Normalize
    for tier in price_tiers:
        price_tiers[tier] /= total_results

    total_categories = sum(categories.values())
    for cat in categories:
        categories[cat] /= total_categories

    for rating in ratings:
        ratings[rating] /= total_results

    bias_detected = False
    bias_details = []

    if price_tiers:
        disparity = max(price_tiers.values()) - min(price_tiers.values())
        if disparity > MAX_PRICE_DISPARITY:
            bias_detected = True
            bias_details.append({
                "type": "price_bias",
                "description": f"Price tier representation disparity: {disparity:.2f}",
                "threshold": MAX_PRICE_DISPARITY,
                "values": dict(price_tiers)
            })

    if categories:
        top_categories = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10])
        for cat, ratio in top_categories.items():
            if ratio > 0.5:
                bias_detected = True
                bias_details.append({
                    "type": "category_dominance",
                    "description": f"Category '{cat}' has dominant representation: {ratio:.2f}",
                    "threshold": 0.5,
                    "value": ratio
                })

    if ratings:
        high_vs_others = ratings.get("high", 0) - (ratings.get("medium", 0) + ratings.get("low", 0))
        if high_vs_others > MAX_RATING_BIAS:
            bias_detected = True
            bias_details.append({
                "type": "rating_bias",
                "description": f"High-rated products are overrepresented: {high_vs_others:.2f}",
                "threshold": MAX_RATING_BIAS,
                "values": dict(ratings)
            })

    bias_score = sum(1 for detail in bias_details)

    bias_results = {
        "bias_detected": bias_detected,
        "bias_score": bias_score,
        "bias_details": bias_details,
        "price_distribution": dict(price_tiers),
        "top_categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]),
        "rating_distribution": dict(ratings),
        "bias_pass": not bias_detected
    }

    with open(BIAS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(bias_results, f, indent=2)

    print("✅ Bias Detection Results:")
    print(f"Bias Detected: {bias_detected}")
    print(f"Bias Score: {bias_score}")
    if bias_details:
        print("Bias Details:")
        for detail in bias_details:
            print(f"- {detail['type']}: {detail['description']}")
    print(f"Bias Check {'PASSED' if not bias_detected else 'FAILED'}")

    return bias_results

if __name__ == "__main__":
    detect_bias()
