from __future__ import annotations

import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, stored_password: str) -> bool:
    if not stored_password:
        return False

    if stored_password == hash_password(password):
        return True

    # Support legacy plain-text rows and let the service upgrade them later.
    return stored_password == password
