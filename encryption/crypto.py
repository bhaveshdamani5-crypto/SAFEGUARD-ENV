import base64
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AESCipher:
    """AES-256-GCM encryption utility for secure secret storage."""

    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            key = self.generate_key()
        self.key = key
        self.aesgcm = AESGCM(self.key)

    @staticmethod
    def generate_key() -> bytes:
        return AESGCM.generate_key(bit_length=256)

    @classmethod
    def from_env(cls) -> "AESCipher":
        encoded_key = os.environ.get("SAFEGUARD_ENV_KEY")
        if encoded_key:
            try:
                key = base64.b64decode(encoded_key)
                return cls(key=key)
            except Exception:
                raise ValueError("SAFEGUARD_ENV_KEY must be a base64 encoded 32-byte AES key")
        return cls()

    def encrypt(self, plaintext: str, associated_data: Optional[bytes] = None) -> str:
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode("utf-8"), associated_data)
        return base64.b64encode(nonce + ciphertext).decode("utf-8")

    def decrypt(self, token: str, associated_data: Optional[bytes] = None) -> str:
        data = base64.b64decode(token.encode("utf-8"))
        nonce = data[:12]
        ciphertext = data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, associated_data).decode("utf-8")


def mask_value(value: str, show_chars: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    return f"{value[:show_chars]}{'*' * (len(value) - show_chars * 2)}{value[-show_chars:]}"
