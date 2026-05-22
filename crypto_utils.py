"""Symmetric encryption helpers for sensitive fields (e.g. Telegram tokens).

Tokens are encrypted with Fernet (AES-128-CBC + HMAC-SHA256). The Fernet key
is derived from the TOKEN_ENCRYPTION_KEY env var if present, otherwise from
SESSION_SECRET. Rotating SESSION_SECRET therefore invalidates stored
ciphertexts — set TOKEN_ENCRYPTION_KEY explicitly in production to decouple
the two.

The EncryptedString TypeDecorator transparently encrypts on write and
decrypts on read. To support migrating existing plaintext rows, decrypt()
returns the raw value when it does not look like a valid Fernet ciphertext.
"""
import base64
import hashlib
import logging
import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.types import String, TypeDecorator

logger = logging.getLogger(__name__)

_fernet_cache: Optional[Fernet] = None


def _get_fernet() -> Fernet:
    global _fernet_cache
    if _fernet_cache is not None:
        return _fernet_cache

    key_source = os.environ.get("TOKEN_ENCRYPTION_KEY") or os.environ.get("SESSION_SECRET")
    if not key_source:
        raise RuntimeError(
            "TOKEN_ENCRYPTION_KEY or SESSION_SECRET must be set for token encryption"
        )

    derived = hashlib.sha256(key_source.encode("utf-8")).digest()
    _fernet_cache = Fernet(base64.urlsafe_b64encode(derived))
    return _fernet_cache


def encrypt_token(plaintext: Optional[str]) -> Optional[str]:
    if plaintext is None or plaintext == "":
        return plaintext
    return _get_fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_token(value: Optional[str]) -> Optional[str]:
    """Decrypt a stored token. Returns the raw value if it is not encrypted
    (so legacy plaintext rows continue to work until migrated)."""
    if value is None or value == "":
        return value
    try:
        return _get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        # Legacy plaintext row — return as-is so the app keeps working.
        return value


class EncryptedString(TypeDecorator):
    """SQLAlchemy column type that transparently encrypts/decrypts a string."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return encrypt_token(value)

    def process_result_value(self, value, dialect):
        return decrypt_token(value)
