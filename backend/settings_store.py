import os
from backend.storage import load_json, save_json

# Determine the base directory of the project (two levels up from this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE = os.path.join(BASE_DIR, "data", "settings.json")

DEFAULT_SETTINGS = {
    "selfHealingMode": True,
    "confidenceThreshold": 50,
    "maxRetryAttempts": 3,
    "showSources": True,
    "topKRetrieval": 5,
    "similarityThreshold": 0.5,
    "queryRewrite": True,
    "criticAgent": True,
    "verificationAgent": True,
    "defaultCollection": "all",
    "autoIndex": True,
    "ocrEnabled": False,
}

def load_settings(user_id):
    payload = load_json(SETTINGS_FILE, {})
    user_settings = payload.get(user_id, {})
    # Merge with defaults
    return {**DEFAULT_SETTINGS, **user_settings}

def save_settings(user_id, settings_dict):
    payload = load_json(SETTINGS_FILE, {})
    # Merge existing settings for user with new updates
    user_settings = payload.get(user_id, {})
    payload[user_id] = {**user_settings, **settings_dict}
    save_json(SETTINGS_FILE, payload)
    return payload[user_id]
