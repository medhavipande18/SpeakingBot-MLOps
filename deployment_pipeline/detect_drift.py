import os
import json
import gzip
import requests
import pandas as pd
from google.cloud import storage
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from config import *
from notifications import send_slack_alert

os.environ["GCP_SA_KEY"] = "credentials/mlops-speakingchatbot-bb5b1137c62b.json"

def download_file_from_url(url: str, local_path: str):
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "wb") as f:
        f.write(response.content)
    print(f"Downloaded latest metadata to {local_path}")
    return local_path

def load_jsonl_gz(path: str):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def load_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def download_gcs_blob(bucket_name: str, blob_name: str, local_path="/tmp/gcs_file.jsonl"):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(local_path)
    print(f"Downloaded GCS file to {local_path}")
    return local_path

def flatten_dataframe(df):
    drop_cols = []
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            drop_cols.append(col)
    if drop_cols:
        print(f"Dropping unhashable columns: {drop_cols}")
        df = df.drop(columns=drop_cols)
    return df

def drop_empty_columns(df1, df2):
    df1_empty = df1.columns[df1.isnull().all()].tolist()
    df2_empty = df2.columns[df2.isnull().all()].tolist()
    to_drop = list(set(df1_empty + df2_empty))
    if to_drop:
        print(f"Dropping empty columns after alignment: {to_drop}")
        df1 = df1.drop(columns=to_drop)
        df2 = df2.drop(columns=to_drop)
    return df1, df2

def align_columns(df1, df2):
    all_columns = sorted(set(df1.columns).union(set(df2.columns)))
    for col in all_columns:
        if col not in df1.columns:
            df1[col] = None
        if col not in df2.columns:
            df2[col] = None
    return df1[all_columns], df2[all_columns]

def detect_drift(reference, current):
    report = Report(metrics=[DataDriftPreset()])

    reference_df = pd.DataFrame(reference)
    current_df = pd.DataFrame(current)

    reference_df = flatten_dataframe(reference_df)
    current_df = flatten_dataframe(current_df)
    
    reference_df, current_df = align_columns(reference_df, current_df)
    reference_df, current_df = drop_empty_columns(reference_df, current_df)

    report.run(reference_data=reference_df, current_data=current_df)

    os.makedirs(os.path.dirname(DRIFT_REPORT_PATH), exist_ok=True)
    report.save_html(DRIFT_REPORT_PATH)
    print(f"Drift report saved to {DRIFT_REPORT_PATH}")

    summary = report.as_dict()
    drift_result = summary["metrics"][0]["result"]
    drifted = drift_result["number_of_drifted_columns"]
    total = drift_result["number_of_columns"]
    ratio = drifted / total

    print(f"Drift detected: {drifted}/{total} columns ({ratio:.2%})")

    if ratio > DRIFT_THRESHOLD:
        send_slack_alert(
            f"{drifted} out of {total} features drifted "
            f"({ratio:.2%}) — exceeds threshold ({DRIFT_THRESHOLD:.2%})"
        )
    else:
        print("Drift within threshold.")

if __name__ == "__main__":
    print("Starting drift detection...")

    latest_file = download_file_from_url(METADATA_URL, TEMP_LOCAL_FILE)
    latest_data = load_jsonl_gz(latest_file)

    gcs_file = download_gcs_blob(GCS_BUCKET_NAME, GCS_BLOB_NAME)
    gcs_data = load_jsonl(gcs_file)

    detect_drift(reference=gcs_data, current=latest_data)