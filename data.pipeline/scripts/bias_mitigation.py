import pandas as pd
import os
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
    """Load JSONL data into a Pandas DataFrame."""
    try:
        return pd.read_json(file_path, lines=True)
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        return pd.DataFrame()


def preprocess_numeric_column(df, column):
    """Convert a column to numeric type, handling errors."""
    if column in df.columns:
        # Convert to float, set invalid values to NaN
        df[column] = pd.to_numeric(df[column], errors="coerce")
        # Replace NaNs with column mean
        df[column].fillna(df[column].mean(), inplace=True)
        logging.info(
            f"Converted {column} to numeric and filled missing values.")


def mitigate_bias(metadata_df, reviews_df):
    """Apply bias mitigation techniques to the dataset."""

    # Convert necessary columns to numeric
    preprocess_numeric_column(metadata_df, "average_rating")
    preprocess_numeric_column(reviews_df, "rating")

    # Adjust ratings for price category bias
    if "price_category" in metadata_df.columns:
        metadata_df["adjusted_rating"] = metadata_df["average_rating"] - \
            metadata_df.groupby("price_category")[
            "average_rating"].transform("mean")
        logging.info("Applied price category bias mitigation.")

    # Adjust ratings for store bias
    if "store" in metadata_df.columns:
        metadata_df["store_adjusted_rating"] = metadata_df["average_rating"] - \
            metadata_df.groupby("store")["average_rating"].transform("mean")
        logging.info("Applied store bias mitigation.")

    # Adjust ratings for verified purchase bias
    if "verified_purchase" in reviews_df.columns:
        reviews_df["verified_adjusted_rating"] = reviews_df["rating"].apply(
            lambda x: x * 0.9 if x > 4 else x)
        logging.info("Applied verified purchase bias mitigation.")

    return metadata_df, reviews_df


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, "data")

    # Load preprocessed data
    metadata_file = os.path.join(
        data_dir, "software_metadata_preprocessed.jsonl")
    reviews_file = os.path.join(
        data_dir, "software_reviews_preprocessed.jsonl")

    metadata_df = load_jsonl(metadata_file)
    reviews_df = load_jsonl(reviews_file)

    if metadata_df.empty or reviews_df.empty:
        logging.error("No data available for bias mitigation.")
        return

    logging.info("Applying bias mitigation strategies...")
    metadata_df, reviews_df = mitigate_bias(metadata_df, reviews_df)

    # Save the mitigated data
    metadata_df.to_json(metadata_file.replace(
        ".jsonl", "_mitigated.jsonl"), orient="records", lines=True)
    reviews_df.to_json(reviews_file.replace(
        ".jsonl", "_mitigated.jsonl"), orient="records", lines=True)

    logging.info("Bias mitigation completed. Files saved.")


if __name__ == "__main__":
    main()
