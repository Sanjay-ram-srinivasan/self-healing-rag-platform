import json
import logging
import os
import threading

import firebase_admin
from firebase_admin import credentials, firestore, storage

logger = logging.getLogger(__name__)

_firebase_lock = threading.Lock()


def _service_account_payload():
    payload = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if payload:
        return json.loads(payload)

    path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    return None


def get_firebase_app():
    with _firebase_lock:
        try:
            return firebase_admin.get_app()
        except ValueError:
            payload = _service_account_payload()
            if payload:
                bucket_name = os.getenv("FIREBASE_BUCKET")
                options = {"storageBucket": bucket_name} if bucket_name else None
                cred = credentials.Certificate(payload)
                return firebase_admin.initialize_app(cred, options)

            default_bucket = os.getenv("FIREBASE_BUCKET")
            options = {"storageBucket": default_bucket} if default_bucket else None
            return firebase_admin.initialize_app(options=options)


def get_firestore_client():
    try:
        app = get_firebase_app()
        return firestore.client(app=app)
    except Exception:
        logger.warning("Firestore client unavailable; using local persistence only.", exc_info=True)
        return None


def get_storage_bucket():
    try:
        app = get_firebase_app()
        return storage.bucket(app=app)
    except Exception:
        logger.warning("Firebase Storage unavailable; using local uploads only.", exc_info=True)
        return None
