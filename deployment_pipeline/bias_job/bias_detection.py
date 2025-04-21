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

# Load env and API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
EMBED_MODEL = "text-embedding-3-small"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.index")
METADATA_PATH = os.path.join(BASE_DIR, "index_metadata.json")
BIAS_RESULTS_PATH = os.path.join(BASE_DIR, "bias_results.json")

# Bias detection thresholds
MAX_PRICE_DISPARITY = 0.3  # Maximum allowable disparity between price tiers
MIN_CATEGORY_REPRESENTATION = 0.1  # Minimum representation for each category
MAX_RATING_BIAS = 0.2  # Maximum allowable bias in rating distribution

def get_query_embedding(text):
    """Get embedding for a query text"""
    response = openai.embeddings.create(
        input=[text],
        model=EMBED_MODEL
    )
    return np.array(response.data[0].embedding, dtype="float32")

def detect_bias():
    """Detect potential biases in the RAG model"""
    # Load FAISS index and metadata
    faiss_index = faiss.read_index(INDEX_PATH)
    
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)
    
    # Prepare test queries for different dimensions
    test_queries = [
        # General product queries
        "recommend software for beginners",
        "best rated software products",
        "affordable software options",
        "premium software solutions",
        # Category-specific queries
        "business software solutions",
        "graphic design software",
        "educational software",
        "productivity tools",
        "coding and development software",
        # Price-sensitive queries
        "cheap software options",
        "expensive professional software",
        "mid-range software products",
        # Rating-sensitive queries
        "top-rated software",
        "popular software products",
        "highest rated software",
    ]
    
    # Analysis dimensions
    price_tiers = defaultdict(int)
    categories = defaultdict(int)
    ratings = defaultdict(int)
    
    total_results = 0
    
    print("Running bias detection tests...")
    
    # Run queries and collect results
    for query in tqdm(test_queries):
        query_vector = get_query_embedding(query).reshape(1, -1)
        k = 5
        D, I = faiss_index.search(query_vector, k)
        
        for idx in I[0]:
            if idx >= 0 and idx < len(metadata_list):
                meta = metadata_list[idx]
                total_results += 1
                
                # Price analysis
                price = meta.get("price", "")
                if isinstance(price, str) and price.startswith("$"):
                    try:
                        price_value = float(price.replace("$", "").replace(",", ""))
                        if price_value < 20:
                            price_tiers["low"] += 1
                        elif price_value < 100:
                            price_tiers["medium"] += 1
                        else:
                            price_tiers["high"] += 1
                    except:
                        pass
                
                # Category analysis
                categories_list = meta.get("categories", [])
                if isinstance(categories_list, list):
                    for category in categories_list:
                        categories[category] += 1
                
                # Rating analysis
                rating = meta.get("average_rating", "")
                if isinstance(rating, (int, float)):
                    if rating < 3:
                        ratings["low"] += 1
                    elif rating < 4:
                        ratings["medium"] += 1
                    else:
                        ratings["high"] += 1
    
    # Normalize counts
    for tier in price_tiers:
        price_tiers[tier] /= total_results
    
    total_categories = sum(categories.values())
    for cat in categories:
        categories[cat] /= total_categories
    
    for rating in ratings:
        ratings[rating] /= total_results
    
    # Detect biases
    bias_detected = False
    bias_details = []
    
    # Price bias detection
    if price_tiers:
        max_price_disparity = max(price_tiers.values()) - min(price_tiers.values())
        if max_price_disparity > MAX_PRICE_DISPARITY:
            bias_detected = True
            bias_details.append({
                "type": "price_bias",
                "description": f"Price tier representation disparity: {max_price_disparity:.2f}",
                "threshold": MAX_PRICE_DISPARITY,
                "values": dict(price_tiers)
            })
    
    # Category bias detection
    if categories:
        # Focus on top 10 categories
        top_categories = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10])
        for cat, ratio in top_categories.items():
            if ratio > 0.5:  # Dominance of a single category
                bias_detected = True
                bias_details.append({
                    "type": "category_dominance",
                    "description": f"Category '{cat}' has dominant representation: {ratio:.2f}",
                    "threshold": 0.5,
                    "value": ratio
                })
    
    # Rating bias detection
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
    
    # Calculate overall bias score
    bias_score = 0
    if bias_details:
        bias_score = sum(1 for detail in bias_details)
    
    # Prepare bias detection results
    bias_results = {
        "bias_detected": bias_detected,
        "bias_score": bias_score,
        "bias_details": bias_details,
        "price_distribution": dict(price_tiers),
        "top_categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]),
        "rating_distribution": dict(ratings),
        "bias_pass": not bias_detected  # Pass if no bias detected
    }
    
    # Save bias detection results
    with open(BIAS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(bias_results, f, indent=2)
    
    print(f"Bias Detection Results:")
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