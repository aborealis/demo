"""
This script generates a password hash and then encodes it in Base64.
"""

from pwdlib import PasswordHash
import base64


PASSWORD = "demo"

password_hash = PasswordHash.recommended()
hash = password_hash.hash(PASSWORD)
print("Your hash for DB:", hash)

hashed_bytes = hash.encode("utf-8")
b64_hashed = base64.b64encode(hashed_bytes).decode("utf-8")
print("Your hash for .env file:", b64_hashed)
