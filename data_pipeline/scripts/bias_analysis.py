import json
import os
import pandas as pd
from fairlearn.metrics import MetricFrame
from sklearn.metrics import accuracy_score
import logging

# Initialize Logging
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(root_dir, "logs")

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_file = os.path.join(logs_dir, "data_pipeline.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def load_jsonl(file_path):
    """Loads a JSONL file into a Pandas DataFrame."""
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return pd.DataFrame()  # Return empty DataFrame if file doesn't exist

    with open(file_path, "r", encoding="utf-8") as file:
        data = [json.loads(line) for line in file]

    return pd.DataFrame(data)


def detect_bias(df, categorical_features, target_feature):
    """
    Detects bias in the dataset by evaluating the distribution of a target feature across categorical slices.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data
    categorical_features (list): List of categorical features to slice data
    target_feature (str): Feature whose distribution will be analyzed
    """
    for feature in categorical_features:
        if feature not in df.columns:
            logging.warning(f"Feature '{feature}' not found in the dataset.")
            continue

        logging.info(f"Analyzing Bias for '{feature}' on '{target_feature}'")
        slice_groups = df.groupby(feature)[target_feature].mean()

        logging.info(f"Bias Analysis for {feature}:\n{slice_groups}\n")

        # If there is a big gap in values, bias may be present
        if slice_groups.max() - slice_groups.min() > 0.2:
            logging.warning(f"Potential Bias Detected in '{feature}'")


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, "data")

    # Load preprocessed data
    metadata_file = os.path.join(
        data_dir, "software_metadata_preprocessed.jsonl")
    reviews_file = os.path.join(
        data_dir, "software_reviews_preprocessed.jsonl")

    metadata_df = load_jsonl(metadata_file)

    # Ensure 'average_rating' is numeric
    if "average_rating" in metadata_df.columns:
        metadata_df["average_rating"] = pd.to_numeric(
            metadata_df["average_rating"], errors="coerce")

    reviews_df = load_jsonl(reviews_file)

    # Check if data was loaded
    if metadata_df.empty or reviews_df.empty:
        logging.error("No data available for bias analysis.")
        return

    logging.info("Data successfully loaded for bias analysis.")

    # Print columns for debugging
    logging.info(f"Metadata Columns: {list(metadata_df.columns)}")
    logging.info(f"Reviews Columns: {list(reviews_df.columns)}")

    # Define categorical features and target
    categorical_features = ["price_category", "store", "verified_purchase"]
    target_feature_metadata = "average_rating"
    target_feature_reviews = "rating"

    # Perform bias detection
    detect_bias(metadata_df, categorical_features, target_feature_metadata)
    detect_bias(reviews_df, categorical_features, target_feature_reviews)


if __name__ == "__main__":
    main()
