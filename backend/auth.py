import os
import json
import threading

_app_lock = threading.Lock()

def _get_firebase_app():
    with _app_lock:
        try:
            return firebase_admin.get_app()
        except ValueError:

            service_account_json = os.getenv(
                "FIREBASE_SERVICE_ACCOUNT_JSON"
            )

            if service_account_json:
                service_account = json.loads(
                    service_account_json
                )

                cred = credentials.Certificate(
                    service_account
                )

                return firebase_admin.initialize_app(
                    cred
                )

            return firebase_admin.initialize_app()