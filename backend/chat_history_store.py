import uuid
from datetime import datetime

from backend.persistence import get_firestore_client
from backend.storage import CHAT_HISTORY_FILE, load_json, save_json


CHAT_COLLECTION = "chat_history"


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

    return chats


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
            "updated_at": datetime.utcnow().isoformat(),
        })

    for stale_user_id in existing_docs - set(chats_by_user.keys()):
        client.collection(CHAT_COLLECTION).document(stale_user_id).delete()


def get_user_chats(user_id):
    chats = [c for c in load_chats() if c.get("user_id") == user_id]
    return sorted(chats, key=lambda x: x.get("updated_at", ""), reverse=True)


def create_chat(user_id, title="New Chat"):
    chats = load_chats()
    chat = {
        "chat_id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "messages": [],
        "updated_at": datetime.utcnow().isoformat(),
    }
    chats.append(chat)
    save_chats(chats)
    return chat


def get_chat(chat_id, user_id):
    for chat in load_chats():
        if chat.get("chat_id") == chat_id and chat.get("user_id") == user_id:
            return chat
    return None


def append_message(chat_id, user_id, message):
    chats = load_chats()
    for chat in chats:
        if chat.get("chat_id") == chat_id and chat.get("user_id") == user_id:
            chat.setdefault("messages", []).append(message)
            chat["updated_at"] = datetime.utcnow().isoformat()
            save_chats(chats)
            return chat
    return None


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
