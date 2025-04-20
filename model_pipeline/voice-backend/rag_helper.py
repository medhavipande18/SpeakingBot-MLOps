import os
import faiss
import json
import numpy as np
import openai
from dotenv import load_dotenv
from sklearn.preprocessing import normalize

# Load env and API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
EMBED_MODEL = "text-embedding-3-small"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.index")
METADATA_PATH = os.path.join(BASE_DIR, "index_metadata.json")

# Load FAISS index and metadata once
faiss_index = faiss.read_index(INDEX_PATH)

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata_list = json.load(f)


def get_query_embedding(text: str) -> np.ndarray:
    response = openai.embeddings.create(
        input=[text],
        model=EMBED_MODEL
    )
    emb = np.array(response.data[0].embedding, dtype="float32").reshape(1, -1)
    return normalize(emb, axis=1)


def fetch_top_k_chunks(query: str, k=3):
    query_vector = get_query_embedding(query)
    D, I = faiss_index.search(query_vector, k)  # D = distances, I = indices

    results = []
    print("Finding relevant matches from RAG")
    for idx, dist in zip(I[0], D[0]):
        if idx >= 0 and idx < len(metadata_list):
            entry = metadata_list[idx]
            print(f"- Title: {entry['title']}, ASIN: {entry['parent_asin']}, Score: {dist:.4f}")
            results.append({
                "parent_asin": entry["parent_asin"],
                "title": entry["title"],
                "chunk_text": entry["chunk_text"],
                "similarity": float(dist)
            })

    return results

