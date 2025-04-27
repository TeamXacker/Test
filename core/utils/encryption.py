# File: core/utils/encryption.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

def encrypt_session(session_str: str, key: str) -> str:
    cipher = AES.new(key.encode()[:32], AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(session_str.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + ct_bytes).decode()

def decrypt_session(enc_str: str, key: str) -> str:
    enc = base64.b64decode(enc_str)
    iv = enc[:16]
    ct = enc[16:]
    cipher = AES.new(key.encode()[:32], AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode()