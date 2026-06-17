import json
import os


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
