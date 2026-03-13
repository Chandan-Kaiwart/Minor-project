import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

# --- MEDIUM RISK DEMO ---
# AES-128 is weakened by Grover's Algorithm.
# Grover's algorithm reduces the security from 128-bit to 64-bit effective security.
# While not immediately "broken" like RSA, 64-bit security is below NIST's 
# recommended long-term security margin.

key = os.urandom(16) # 128-bit key
iv = os.urandom(16)
cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

# SHA-256 is also in the medium category as quantum computers might find 
# collisions more easily, though it's much safer than SHA-1.
hash_256 = hashlib.sha256(b"medium_security_data").hexdigest()

print("Using AES-128 which is weakened by Grover's Algorithm.")
