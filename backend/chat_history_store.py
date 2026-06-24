import uuid
from datetime import datetime

from backend.persistence import get_firestore_client
from backend.storage import CHAT_HISTORY_FILE, load_json, save_json


CHAT_COLLECTION = "chat_history"


def _utc_now():
    return datetime.utcnow().isoformat()


def _normalize_chat(chat):
    changed = False
    if not chat.get("created_at"):
        first_message = next((message for message in chat.get("messages", []) if message.get("timestamp")), None)
        chat["created_at"] = first_message.get("timestamp") if first_message else chat.get("updated_at") or _utc_now()
        changed = True
    if not chat.get("updated_at"):
        chat["updated_at"] = chat["created_at"]
        changed = True
    return chat, changed


def _local_payload():
    return load_json(CHAT_HISTORY_FILE, {"chats": []})


def _remote_doc_ref(user_id):
    client = get_firestore_client()
    if not client:
        return None
    return client.collection(CHAT_COLLECTION).document(user_id)


def sync_chats_from_firestore(user_id=None):
    client = get_firestore_client()
    if not client:
        return []

    chats = []
    if user_id:
        snapshot = client.collection(CHAT_COLLECTION).document(user_id).get()
        if snapshot.exists:
            chats = snapshot.to_dict().get("chats", [])
    else:
        for doc in client.collection(CHAT_COLLECTION).stream():
            chats.extend(doc.to_dict().get("chats", []))

    if chats:
        save_json(CHAT_HISTORY_FILE, {"chats": chats})
    return chats


def load_chats():
    payload = _local_payload()
    chats = payload.get("chats", [])

    remote_chats = sync_chats_from_firestore()
    if remote_chats:
        chats = remote_chats

    normalized_chats = []
    changed = False
    for chat in chats:
        normalized_chat, chat_changed = _normalize_chat(chat)
        normalized_chats.append(normalized_chat)
        changed = changed or chat_changed
    if changed:
        save_chats(normalized_chats)
    return normalized_chats


def save_chats(chats):
    save_json(CHAT_HISTORY_FILE, {"chats": chats})
    client = get_firestore_client()
    if not client:
        return

    chats_by_user = {}
    for chat in chats:
        user_id = chat.get("user_id")
        if not user_id:
            continue
        chats_by_user.setdefault(user_id, []).append(chat)

    existing_docs = {
        doc.id for doc in client.collection(CHAT_COLLECTION).stream()
    }

    for user_id, user_chats in chats_by_user.items():
        client.collection(CHAT_COLLECTION).document(user_id).set({
            "user_id": user_id,
            "chats": user_chats,
            "updated_at": _utc_now(),
        })

    for stale_user_id in existing_docs - set(chats_by_user.keys()):
        client.collection(CHAT_COLLECTION).document(stale_user_id).delete()


def get_user_chats(user_id):
    chats = [c for c in load_chats() if c.get("user_id") == user_id]
    return sorted(chats, key=lambda x: x.get("updated_at", ""), reverse=True)


def update_chat(chat_id: str, user_id: str, title: str | None = None, pinned: bool | None = None) -> bool:
    """Update chat metadata such as title or pinned flag.
    Returns True if chat was found and updated.
    """
    chats = load_chats()
    updated = False
    for chat in chats:
        if chat.get("chat_id") == chat_id and chat.get("user_id") == user_id:
            if title is not None:
                chat["title"] = title
            if pinned is not None:
                chat["pinned"] = pinned
            chat["updated_at"] = _utc_now()
            updated = True
            break
    if updated:
        save_chats(chats)
    return updated


def create_chat(user_id, title="New Chat", collection_id=None):
    chats = load_chats()
    timestamp = _utc_now()
    chat = {
        "chat_id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "collection_id": collection_id,
        "messages": [],
        "pinned": False,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    chats.append(chat)
    save_chats(chats)
    return chat


def get_chat(chat_id, user_id):
    for chat in load_chats():
        if chat.get("chat_id") == chat_id and chat.get("user_id") == user_id:
            return chat
    return None


def append_message(chat_id, user_id, message, collection_id=None):
    chats = load_chats()
    for chat in chats:
        if chat.get("chat_id") == chat_id and chat.get("user_id") == user_id:
            chat.setdefault("messages", []).append(message)
            if collection_id is not None:
                chat["collection_id"] = collection_id
            chat["updated_at"] = _utc_now()
            save_chats(chats)
            return chat
    return None


def search_chats(user_id: str, query: str) -> list:
    """Search chats by title substring for a given user."""
    lower_q = query.lower()
    return [c for c in get_user_chats(user_id) if lower_q in c.get("title", "").lower()]


def delete_chat(chat_id, user_id):
    chats = load_chats()
    next_chats = [
        chat for chat in chats
        if not (chat.get("chat_id") == chat_id and chat.get("user_id") == user_id)
    ]
    if len(next_chats) != len(chats):
        save_chats(next_chats)
        return True
    return False
