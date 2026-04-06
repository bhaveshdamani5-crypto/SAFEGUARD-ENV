import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Optional

class SecureVault:
    """
    A simulated zero-knowledge vault for hackathon demonstration. 
    It dynamically generates an AES-256-GCM key and provides robust encryption 
    for secrets and honeypots in memory.
    """
    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            # Generate a 256-bit key
            self.key = AESGCM.generate_key(bit_length=256)
        else:
            self.key = key
        self.aesgcm = AESGCM(self.key)

    def encrypt_secret(self, plaintext: str) -> str:
        """Encrypts a string and returns a base64 encoded ciphertext including the nonce."""
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    def decrypt_secret(self, encoded_ciphertext: str) -> str:
        """Decrypts a base64 encoded payload holding nonce + ciphertext."""
        data = base64.b64decode(encoded_ciphertext.encode('utf-8'))
        nonce = data[:12]
        ciphertext = data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')

# Global default vault (to demonstrate secure key creation on boot)
global_vault = SecureVault()
