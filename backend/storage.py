import json
import os
import shutil

from backend.persistence import get_storage_bucket


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")
COLLECTIONS_FILE = os.path.join(DATA_DIR, "collections.json")
DOCUMENTS_META_FILE = os.path.join(DATA_DIR, "documents_meta.json")


def ensure_parent(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def load_json(path, default):
    ensure_parent(path)
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default


def save_json(path, payload):
    ensure_parent(path)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def upload_file_to_storage(local_path, blob_path):
    bucket = get_storage_bucket()
    if not bucket or not os.path.exists(local_path):
        return False

    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_path)
    return True


def download_blob_to_file(blob_path, local_path):
    bucket = get_storage_bucket()
    if not bucket:
        return False

    blob = bucket.blob(blob_path)
    if not blob.exists():
        return False

    ensure_parent(local_path)
    blob.download_to_filename(local_path)
    return True


def sync_folder_from_storage(prefix, destination_dir):
    bucket = get_storage_bucket()
    if not bucket:
        return 0

    os.makedirs(destination_dir, exist_ok=True)
    restored = 0
    for blob in bucket.list_blobs(prefix=prefix):
        filename = os.path.basename(blob.name)
        if not filename:
            continue
        local_path = os.path.join(destination_dir, filename)
        if os.path.exists(local_path):
            continue
        blob.download_to_filename(local_path)
        restored += 1
    return restored
