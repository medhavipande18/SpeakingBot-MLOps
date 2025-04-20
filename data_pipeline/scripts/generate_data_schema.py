import os
import json
import time
import pandas as pd
import logging
import great_expectations as ge
import concurrent.futures

# Define Paths
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(root_dir, "data")
logs_dir = os.path.join(root_dir, "logs")

# Ensure logs directory exists
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Initialize Logging
log_file = os.path.join(logs_dir, "data_schema_statistics.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Data Schema & Statistics Generation Started")

metadata_file = os.path.join(data_dir, "software_metadata_preprocessed.jsonl")
reviews_file = os.path.join(data_dir, "software_reviews_preprocessed.jsonl")


def load_data(file_path, chunksize=10000):
    """
    Loads JSONL file efficiently in chunks and logs progress.
    """
    start_time = time.time()

    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return None

    # Get total record count
    total_records = sum(1 for _ in open(file_path, "r", encoding="utf-8"))
    data = []
    records_processed = 0

    try:
        for chunk in pd.read_json(file_path, lines=True, chunksize=chunksize):
            data.append(chunk)
            records_processed += len(chunk)
            logging.info(
                f"Progress: {records_processed}/{total_records} records processed for {file_path}")

        df = pd.concat(data, ignore_index=True)
        logging.info(
            f"Successfully loaded {file_path} ({df.shape[0]} rows) in {time.time() - start_time:.2f} seconds")
        return df

    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        return None


def extract_schema(df, file_name):
    """
    Extracts schema using DataFrame dtypes.
    """
    start_time = time.time()
    schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
    schema_file = os.path.join(data_dir, f"{file_name}_schema.json")

    try:
        with open(schema_file, "w") as f:
            json.dump(schema, f, indent=4)

        logging.info(
            f"Schema saved to {schema_file} (Time Taken: {time.time() - start_time:.2f} sec)")
    except Exception as e:
        logging.error(f"Error saving schema {file_name}: {e}")


def generate_statistics(df, file_name, chunksize=10000):
    """
    Generates statistics efficiently in chunks with progress logging.
    """
    start_time = time.time()
    stats = {"numeric": {}, "categorical": {}}
    total_records = len(df)
    records_processed = 0

    try:
        # Identify numeric and categorical columns
        numeric_cols = df.select_dtypes(include=["number"]).columns
        categorical_cols = df.select_dtypes(include=["O", "category"]).columns

        # Ensure all list/dictionary-type columns are converted to strings before processing
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                df[col] = df[col].apply(lambda x: str(
                    x) if isinstance(x, (list, dict)) else x)

        # Process in chunks
        for chunk_start in range(0, total_records, chunksize):
            chunk = df.iloc[chunk_start:chunk_start + chunksize]
            records_processed += len(chunk)

            # Compute numeric statistics per chunk
            if len(numeric_cols) > 0:
                numeric_stats = chunk[numeric_cols].agg(
                    ["mean", "std", "min", "max"]).to_dict()
                for key, val in numeric_stats.items():
                    if key not in stats["numeric"]:
                        stats["numeric"][key] = val
                    else:
                        # Update stats incrementally (Weighted Average for mean)
                        stats["numeric"][key]["mean"] = (
                            (stats["numeric"][key]["mean"] * (records_processed - len(chunk)) +
                             val["mean"] * len(chunk)) / records_processed
                        )
                        stats["numeric"][key]["std"] = val["std"]
                        stats["numeric"][key]["min"] = min(
                            stats["numeric"][key]["min"], val["min"])
                        stats["numeric"][key]["max"] = max(
                            stats["numeric"][key]["max"], val["max"])

            # Compute categorical statistics per chunk
            if len(categorical_cols) > 0:
                for col in categorical_cols:
                    value_counts = chunk[col].value_counts().to_dict()
                    if col not in stats["categorical"]:
                        stats["categorical"][col] = value_counts
                    else:
                        # Merge counts
                        for k, v in value_counts.items():
                            stats["categorical"][col][k] = stats["categorical"][col].get(
                                k, 0) + v

            # Log progress
            logging.info(
                f"Processed {records_processed}/{total_records} records for {file_name}")

        # Save final statistics
        stats_file = os.path.join(data_dir, f"{file_name}_statistics.json")
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=4)

        logging.info(
            f"Statistics saved to {stats_file} (Time Taken: {time.time() - start_time:.2f} sec)")

    except Exception as e:
        logging.error(f"Error generating statistics for {file_name}: {e}")


def validate_schema(df, expected_schema):
    """
    Validates schema using Great Expectations.
    """
    start_time = time.time()
    ge_df = ge.from_pandas(df)
    results = {}

    try:
        for col, dtype in expected_schema.items():
            if col in df.columns:
                results[col] = ge_df.expect_column_values_to_be_of_type(
                    col, dtype)
            else:
                results[col] = f"Column '{col}' missing"

        logging.info(
            f"Schema validation completed in {time.time() - start_time:.2f} sec")
        return results

    except Exception as e:
        logging.error(f"Error during schema validation: {e}")
        return {}


if __name__ == "__main__":
    start_execution_time = time.time()

    metadata_df = load_data(metadata_file)
    reviews_df = load_data(reviews_file)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        if metadata_df is not None:
            executor.submit(extract_schema, metadata_df, "metadata")
            executor.submit(generate_statistics, metadata_df, "metadata")

        if reviews_df is not None:
            executor.submit(extract_schema, reviews_df, "reviews")
            executor.submit(generate_statistics, reviews_df, "reviews")

    logging.info(
        f"Data Schema & Statistics Generation Completed in {time.time() - start_execution_time:.2f} seconds")
