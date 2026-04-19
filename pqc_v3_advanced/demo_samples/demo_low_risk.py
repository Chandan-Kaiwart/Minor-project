import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

# --- LOW RISK DEMO ---
# AES-256 is generally considered quantum-resistant for the foreseeable future.
# While Grover's algorithm halves its security strength, it still provides 128 bits 
# of quantum security, which is well above the safety threshold.

key = os.urandom(32) # 256-bit key
iv = os.urandom(16)
cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
encryptor = cipher.encryptor()

# Using SHA-512 is also considered safe for now.
safe_hash = hashlib.sha512(b"safe_data").hexdigest()

print("Using quantum-resistant AES-256 and SHA-512")
