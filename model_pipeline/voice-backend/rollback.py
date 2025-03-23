# rollback.py
import shutil
import os

def rollback_index():
    backup_dir = "backups"
    index_file = "faiss_index.index"
    metadata_file = "index_metadata.json"

    if not os.path.exists(backup_dir):
        print("No backup directory found.")
        return

    try:
        shutil.copy(os.path.join(backup_dir, "faiss_index.index"), index_file)
        shutil.copy(os.path.join(backup_dir, "index_metadata.json"), metadata_file)
        print("✅ Rollback successful. Previous model restored.")
    except Exception as e:
        print("Rollback failed:", e)

if __name__ == "__main__":
    rollback_index()
