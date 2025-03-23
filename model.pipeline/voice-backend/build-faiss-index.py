# ======= Updated build-faiss-index.py (FAISS builder with product logging) =======
import json
import os
import faiss
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv
import openai
from sklearn.preprocessing import normalize
from google.cloud import storage

def download_from_gcs(bucket_name, source_blob_name, destination_file_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {source_blob_name} to {destination_file_name}")

# Load OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
EMBED_MODEL = "text-embedding-3-small"
#META_PATH = "data/meta_software.json"
#REVIEWS_PATH = "data/software.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_INDEX = os.path.join(BASE_DIR, "faiss_index.index")
OUTPUT_METADATA = os.path.join(BASE_DIR, "index_metadata.json")


def load_data():
    bucket_name = "speaking-chatbot-data"
    meta_blob = "software_metadata_preprocessed.jsonl"
    reviews_blob = "software_reviews_preprocessed.jsonl"

    local_meta = os.path.join(BASE_DIR, "tmp_meta.jsonl")
    local_reviews = os.path.join(BASE_DIR, "tmp_reviews.jsonl")

    # Download from GCS
    download_from_gcs(bucket_name, meta_blob, local_meta)
    download_from_gcs(bucket_name, reviews_blob, local_reviews)

    # Read .jsonl files
    def read_jsonl(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return [json.loads(line.strip()) for line in f if line.strip()]

    meta = read_jsonl(local_meta)
    reviews = read_jsonl(local_reviews)

    return meta, reviews


def clean_text(text):
    if isinstance(text, list):
        text = " ".join(text)
    elif not isinstance(text, str):
        text = str(text)
    return text.replace("\n", " ").replace("\r", " ").strip()


def group_reviews_by_asin(reviews):
    grouped = {}
    for r in reviews:
        asin = r.get("parent_asin")
        if not asin:
            continue
        if asin not in grouped:
            grouped[asin] = []
        if r.get("verified_purchase") and r.get("text"):
            grouped[asin].append(r["text"])
    return grouped


def build_chunks(meta, review_groups):
    chunks = []
    metadata = []

    for entry in meta:
        asin = entry.get("parent_asin")
        if not asin:
            continue

        title = entry.get("title", "")
        description = entry.get("description", "")
        features = entry.get("features", [])
        categories = entry.get("categories", [])
        details = entry.get("details", {})
        rating = entry.get("average_rating", "")
        price = entry.get("price", "")

        features_str = ", ".join(features) if isinstance(features, list) else features
        categories_str = ", ".join(categories) if isinstance(categories, list) else categories
        details_str = "\n".join([f"{k}: {v}" for k, v in details.items()]) if isinstance(details, dict) else str(details)

        reviews = review_groups.get(asin, [])
        reviews_str = "\n".join(reviews[:5])

        full_text = f"""Title: {clean_text(title)}
Rating: {rating}
Price: {price}
Categories: {categories_str}
Features: {features_str}
Description: {clean_text(description)}
Details:
{details_str}

Top Reviews:
{reviews_str}
"""

        chunks.append(full_text)
        metadata.append({
            "parent_asin": asin,
            "title": title,
            "chunk_text": full_text
        })

    return chunks, metadata


def get_embedding(text):
    response = openai.embeddings.create(
        input=[text],
        model=EMBED_MODEL
    )
    return np.array(response.data[0].embedding, dtype="float32")


def build_faiss_index(text_chunks):
    dim = len(get_embedding("test"))
    index = faiss.IndexFlatL2(dim)
    vectors = []

    print("Embedding and indexing documents...")
    for i, text in enumerate(tqdm(text_chunks)):
        emb = get_embedding(text)
        vectors.append(emb)

    vectors_np = np.array(vectors, dtype="float32")
    vectors_np = normalize(vectors_np, axis=1)
    index.add(vectors_np)
    return index


SUBSET_SIZE = 500

def main():
    meta, reviews = load_data()
    meta_subset = meta[:SUBSET_SIZE]
    
    for i, item in enumerate(meta_subset):
        print(f"{i+1} {item.get('title', 'Untitled Product')}")

    selected_asins = {entry["parent_asin"] for entry in meta_subset if "parent_asin" in entry}
    filtered_reviews = [r for r in reviews if r.get("parent_asin") in selected_asins]

    review_groups = group_reviews_by_asin(filtered_reviews)
    text_chunks, metadata = build_chunks(meta_subset, review_groups)
    index = build_faiss_index(text_chunks)

    print(f"\nSaving FAISS index to: {OUTPUT_INDEX}")
    faiss.write_index(index, OUTPUT_INDEX)

    print(f"Saving metadata to: {OUTPUT_METADATA}")
    with open(OUTPUT_METADATA, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("Index build complete.")


if __name__ == "__main__":
    main()