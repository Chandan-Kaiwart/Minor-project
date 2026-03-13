from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec
import hashlib

# --- CRITICAL RISK DEMO ---
# RSA, ECC, and DSA are COMPLETELY BROKEN by Shor's Algorithm.
# A large-scale quantum computer can factor large integers and solve discrete logs
# in polynomial time, rendering these algorithms useless.

# 1. RSA (Critical)
private_key_rsa = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# 2. Elliptic Curve (Critical)
private_key_ecc = ec.generate_private_key(ec.SECP256R1())

# 3. Legacy MD5/SHA1 (Critical)
bad_hash = hashlib.md5(b"broken").hexdigest()
legacy_hash = hashlib.sha1(b"insecure").hexdigest()

print("CRITICAL: RSA and ECC detected. These provide 0-bit security against Shor's Algorithm.")