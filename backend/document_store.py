import os
import shutil

from backend.persistence import get_storage_bucket

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))


def save_file_locally(file_path: str, filename: str) -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    dest = os.path.join(UPLOAD_DIR, filename)
    if os.path.abspath(file_path) != os.path.abspath(dest):
        shutil.copyfile(file_path, dest)


def upload_to_storage(filename: str) -> bool:
    bucket = get_storage_bucket()
    local_path = os.path.join(UPLOAD_DIR, filename)
    if not bucket or not os.path.exists(local_path):
        return False
    blob = bucket.blob(f"uploads/{filename}")
    blob.upload_from_filename(local_path)
    return True


def delete_from_storage(filename: str) -> bool:
    bucket = get_storage_bucket()
    if not bucket:
        return False
    blob = bucket.blob(f"uploads/{filename}")
    if not blob.exists():
        return False
    blob.delete()
    return True


def sync_from_storage() -> int:
    bucket = get_storage_bucket()
    if not bucket:
        return 0

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    restored = 0
    for blob in bucket.list_blobs(prefix="uploads/"):
        filename = os.path.basename(blob.name)
        if not filename:
            continue
        local_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(local_path):
            continue
        blob.download_to_filename(local_path)
        restored += 1
    return restored
