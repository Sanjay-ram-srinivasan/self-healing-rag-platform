import uuid

from backend.storage import COLLECTIONS_FILE, load_json, save_json


def load_collections():
    payload = load_json(COLLECTIONS_FILE, {"collections": []})
    collections = payload.get("collections", [])

    if not collections:
        collections = [
            _build_collection("AI Notes"),
            _build_collection("Research Papers"),
            _build_collection("College Documents"),
        ]
        save_collections(collections)

    return collections


def save_collections(collections):
    save_json(COLLECTIONS_FILE, {"collections": collections})


def create_collection(name, user_id):
    collections = load_collections()
    collection = _build_collection(name, user_id=user_id)
    collections.append(collection)
    save_collections(collections)
    return collection


def delete_collection(collection_id):
    collections = load_collections()
    next_items = [item for item in collections if item["id"] != collection_id]
    save_collections(next_items)
    return len(next_items) != len(collections)


def find_collection(collection_id):
    for collection in load_collections():
        if collection["id"] == collection_id:
            return collection
    return None


def _build_collection(name, user_id="system"):
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "user_id": user_id,
    }
