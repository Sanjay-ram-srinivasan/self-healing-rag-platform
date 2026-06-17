import uuid
from datetime import datetime

from backend.storage import CHAT_HISTORY_FILE, load_json, save_json

def load_chats():
    payload = load_json(CHAT_HISTORY_FILE, {"chats": []})
    return payload.get("chats", [])

def save_chats(chats):
    save_json(CHAT_HISTORY_FILE, {"chats": chats})

def get_user_chats(user_id):
    chats = load_chats()
    user_chats = [c for c in chats if c.get("user_id") == user_id]
    return sorted(user_chats, key=lambda x: x.get("updated_at", ""), reverse=True)

def create_chat(user_id, title="New Chat"):
    chats = load_chats()
    chat = {
        "chat_id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "messages": [],
        "updated_at": datetime.now().isoformat()
    }
    chats.append(chat)
    save_chats(chats)
    return chat

def get_chat(chat_id, user_id):
    for c in load_chats():
        if c.get("chat_id") == chat_id and c.get("user_id") == user_id:
            return c
    return None

def append_message(chat_id, user_id, message):
    chats = load_chats()
    for c in chats:
        if c.get("chat_id") == chat_id and c.get("user_id") == user_id:
            c["messages"].append(message)
            c["updated_at"] = datetime.now().isoformat()
            save_chats(chats)
            return c
    return None

def delete_chat(chat_id, user_id):
    chats = load_chats()
    next_chats = [
        c for c in chats
        if not (c.get("chat_id") == chat_id and c.get("user_id") == user_id)
    ]
    if len(next_chats) != len(chats):
        save_chats(next_chats)
        return True
    return False
