import os

def test_files_downloaded():
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, "data")

    review_file = os.path.join(data_dir, "software_reviews.jsonl.gz")
    metadata_file = os.path.join(data_dir, "software_metadata.jsonl.gz")

    assert os.path.exists(review_file), f"Missing file: {review_file}"
    assert os.path.exists(metadata_file), f"Missing file: {metadata_file}"
