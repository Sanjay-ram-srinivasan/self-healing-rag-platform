"""
document_store.py
-----------------
All Firebase Storage and Firestore document-persistence helpers.

Storage layout
  Firebase Storage : uploads/<filename>
  Firestore        : collection "document_files" / doc "<filename>"
                     Fields: user_id, filename, pages, chunks, size_bytes,
                             collection_id, ocr_used, uploaded_at, status,
                             reindexed_at (optional)

Every upload writes:
  1. local disk  (uploads/ dir – ephemeral, used while the process runs)
  2. Firebase Storage (permanent)
  3. Firestore document_files/<filename>  (permanent metadata)

On startup the app calls sync_from_storage() which:
  1. Downloads any Storage blobs not present locally
  2. Returns a list of (filename, meta) pairs for vector-store rebuilding
"""

import logging
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from backend.persistence import get_firestore_client, get_storage_bucket

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))

_STORAGE_PREFIX = "uploads/"
_FS_COLLECTION   = "document_files"
_FIRESTORE_LIST_TIMEOUT_SECONDS = 20


def _stream_document_meta(client) -> dict[str, dict]:
    docs = client.collection(_FS_COLLECTION).stream()
    result = {}
    for doc in docs:
        data = doc.to_dict()
        fname = data.get("filename") or doc.id
        result[fname] = data
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Firebase Storage helpers
# ─────────────────────────────────────────────────────────────────────────────

def upload_to_storage(filename: str) -> bool:
    """Upload a file from the local uploads directory to Firebase Storage."""
    bucket = get_storage_bucket()
    local_path = os.path.join(UPLOAD_DIR, filename)
    if not bucket:
        logger.warning("[Storage] Firebase Storage unavailable; skipping upload of %s.", filename)
        return False
    if not os.path.exists(local_path):
        logger.error("[Storage] Local file not found for upload: %s", local_path)
        return False
    try:
        blob = bucket.blob(f"{_STORAGE_PREFIX}{filename}")
        blob.upload_from_filename(local_path)
        logger.info("[Storage] Uploaded %s to Firebase Storage.", filename)
        return True
    except Exception:
        logger.error("[Storage] Failed to upload %s to Firebase Storage.", filename, exc_info=True)
        return False


def delete_from_storage(filename: str) -> bool:
    """Delete a file from Firebase Storage. Returns True if deleted or not found."""
    bucket = get_storage_bucket()
    if not bucket:
        logger.warning("[Storage] Firebase Storage unavailable; cannot delete %s.", filename)
        return False
    try:
        blob = bucket.blob(f"{_STORAGE_PREFIX}{filename}")
        if blob.exists():
            blob.delete()
            logger.info("[Storage] Deleted %s from Firebase Storage.", filename)
        return True
    except Exception:
        logger.error("[Storage] Failed to delete %s from Firebase Storage.", filename, exc_info=True)
        return False


def _download_from_storage(filename: str, local_path: str) -> bool:
    """Download a single blob from Firebase Storage to a local path."""
    bucket = get_storage_bucket()
    if not bucket:
        return False
    try:
        blob = bucket.blob(f"{_STORAGE_PREFIX}{filename}")
        if not blob.exists():
            logger.warning("[Storage] Blob not found in Firebase Storage: %s", filename)
            return False
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
        logger.info("[Storage] Downloaded %s from Firebase Storage.", filename)
        return True
    except Exception:
        logger.error("[Storage] Failed to download %s.", filename, exc_info=True)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Firestore metadata helpers  (one Firestore doc per uploaded file)
# ─────────────────────────────────────────────────────────────────────────────

def save_document_meta(filename: str, meta: dict) -> bool:
    """
    Persist per-document metadata to Firestore.
    Returns True on success, False if Firestore is unavailable.
    """
    client = get_firestore_client()
    if not client:
        logger.warning("[Firestore] Unavailable; metadata for %s not saved remotely.", filename)
        return False
    try:
        doc_ref = client.collection(_FS_COLLECTION).document(filename)
        doc_ref.set({**meta, "filename": filename})
        logger.info("[Firestore] Saved metadata for %s.", filename)
        return True
    except Exception:
        logger.error("[Firestore] Failed to save metadata for %s.", filename, exc_info=True)
        return False


def delete_document_meta(filename: str) -> bool:
    """Delete per-document metadata from Firestore."""
    client = get_firestore_client()
    if not client:
        logger.warning("[Firestore] Unavailable; cannot delete metadata for %s.", filename)
        return False
    try:
        client.collection(_FS_COLLECTION).document(filename).delete()
        logger.info("[Firestore] Deleted metadata for %s.", filename)
        return True
    except Exception:
        logger.error("[Firestore] Failed to delete metadata for %s.", filename, exc_info=True)
        return False


def get_document_meta(filename: str) -> dict | None:
    """Fetch metadata for a single document from Firestore. Returns None if not found."""
    client = get_firestore_client()
    if not client:
        return None
    try:
        doc = client.collection(_FS_COLLECTION).document(filename).get()
        return doc.to_dict() if doc.exists else None
    except Exception:
        logger.error("[Firestore] Failed to fetch metadata for %s.", filename, exc_info=True)
        return None


def list_all_document_meta() -> dict[str, dict]:
    """
    Return a dict mapping filename → metadata for every document stored in
    Firestore. Used during startup to discover what should be on disk.
    """
    client = get_firestore_client()
    if not client:
        logger.warning("[Firestore] Unavailable; cannot list document metadata.")
        return {}
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_stream_document_meta, client)
            result = future.result(timeout=_FIRESTORE_LIST_TIMEOUT_SECONDS)
        logger.info("[Firestore] Listed %d document metadata records.", len(result))
        return result
    except FuturesTimeoutError:
        logger.error("[Firestore] Timed out listing document metadata after %ss.", _FIRESTORE_LIST_TIMEOUT_SECONDS)
        return {}
    except Exception:
        logger.error("[Firestore] Failed to list document metadata.", exc_info=True)
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# Startup restore
# ─────────────────────────────────────────────────────────────────────────────

def sync_from_storage() -> list[tuple[str, dict]]:
    """
    Called once at startup.

    1. Reads ALL document metadata from Firestore.
    2. For each known file, downloads it from Firebase Storage if not already
       present on the local disk.
    3. Returns a list of (filename, meta) tuples for every file that is now
       present locally, so the caller can rebuild the vector store.

    Falls back gracefully: if Firebase is unavailable it returns an empty list
    and the app continues normally (local files, if any, are used as-is).
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    all_meta = list_all_document_meta()
    if not all_meta:
        # Try a raw Storage listing as a last resort (no metadata path)
        all_meta = _discover_from_storage_only()

    restored = []
    for filename, meta in all_meta.items():
        local_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(local_path):
            ok = _download_from_storage(filename, local_path)
            if not ok:
                logger.warning("[Startup] Could not restore %s from Firebase Storage.", filename)
                continue
            logger.info("[Startup] Restored %s from Firebase Storage.", filename)
        restored.append((filename, meta))

    logger.info("[Startup] %d/%d documents ready locally.", len(restored), len(all_meta))
    return restored


def _discover_from_storage_only() -> dict[str, dict]:
    """
    Fallback: if Firestore has no metadata records, list Firebase Storage blobs
    and return stub metadata so files can still be downloaded and re-indexed.
    """
    bucket = get_storage_bucket()
    if not bucket:
        return {}
    result = {}
    try:
        for blob in bucket.list_blobs(prefix=_STORAGE_PREFIX):
            filename = os.path.basename(blob.name)
            if not filename:
                continue
            result[filename] = {
                "filename": filename,
                "status": "indexed",
                "user_id": None,
                "pages": 0,
                "chunks": 0,
            }
        logger.info("[Startup] Discovered %d blobs from Storage (no Firestore metadata).", len(result))
    except Exception:
        logger.error("[Startup] Failed to list Storage blobs.", exc_info=True)
    return result
