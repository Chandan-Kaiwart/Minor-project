#!/usr/bin/env python3
"""
=============================================================
  PQCRA IoT Sensor Module — PQC-Hardened Edition
  Runs on Android Phone via Termux (Flask Server)
  
  PROBLEM STATEMENT 2: Securing IoT Devices from Quantum Attacks
  
  BEFORE /upgrade_pqc:
    - All endpoints are OPEN (Legacy ECC mode)
    - Anyone with the IP can access /status, /camera, etc.
    - This demonstrates the VULNERABILITY
  
  AFTER /upgrade_pqc:
    - Device generates a PQC Session Token (ML-KEM derived)
    - ALL endpoints now REQUIRE this token in the header
    - Without token → HTTP 403 ACCESS DENIED
    - This demonstrates the SOLUTION (Device-Level Security)
=============================================================
"""

from flask import Flask, jsonify, request, Response
import random, time, hashlib, os, json

app = Flask(__name__)

# ====== DEVICE STATE ======
device_state = {
    "crypto_status": "ECC (LEGACY)",
    "pqc_active": False,
    "pqc_token": None,          # Generated on upgrade
    "pqc_upgrade_time": None,
    "device_id": "ANDROID_EDGE_01",
    "firmware": "v1.0-LEGACY"
}

# ====== PQC TOKEN GENERATOR (ML-KEM Derived) ======
def generate_pqc_token():
    """Simulate ML-KEM Key Encapsulation to derive a shared session token"""
    # In production: This would be a real Kyber/ML-KEM key exchange
    # For demo: We derive a strong token from lattice-simulated entropy
    seed = f"MLKEM-768-{time.time()}-{random.randint(0, 2**32)}"
    token = hashlib.sha256(seed.encode()).hexdigest()
    return token

# ====== PQC AUTH MIDDLEWARE ======
def require_pqc_auth():
    """
    If PQC is active, EVERY request must carry the PQC token.
    This is the CORE of Problem Statement 2:
    Even if hacker knows the IP, they CANNOT access the device.
    """
    if not device_state["pqc_active"]:
        return None  # ECC mode: No auth required (VULNERABLE!)
    
    # PQC MODE: Check for token
    auth_token = request.headers.get("X-PQC-Token", "")
    if auth_token != device_state["pqc_token"]:
        print(f"[PQC-SHIELD] ⛔ UNAUTHORIZED ACCESS BLOCKED from {request.remote_addr}")
        print(f"[PQC-SHIELD]    Provided Token: {auth_token[:16]}..." if auth_token else "[PQC-SHIELD]    No Token Provided!")
        return jsonify({
            "error": "ACCESS_DENIED",
            "reason": "PQC-SHIELD ACTIVE: ML-KEM Authentication Required",
            "device": device_state["device_id"],
            "crypto": "ML-KEM-768 (QUANTUM-SAFE)",
            "message": "This device is protected by Post-Quantum Cryptography. Unauthorized access is permanently blocked."
        }), 403
    
    return None  # Token verified — access granted

# ====== SENSOR DATA GENERATOR ======
def get_sensor_data():
    return {
        "temperature": round(random.uniform(22.0, 35.0), 1),
        "humidity": round(random.uniform(40.0, 70.0), 1),
        "cpu_usage": round(random.uniform(5.0, 45.0), 1),
        "battery": random.randint(20, 100),
        "signal_strength": random.randint(-80, -40),
        "crypto_status": device_state["crypto_status"],
        "threat_level": "HIGH" if not device_state["pqc_active"] else "NONE",
        "device_id": device_state["device_id"],
        "firmware": device_state["firmware"],
        "pqc_active": device_state["pqc_active"],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

# ====== ENDPOINTS ======

@app.route('/status', methods=['GET'])
def status():
    """Device telemetry — OPEN in ECC mode, LOCKED in PQC mode"""
    auth_check = require_pqc_auth()
    if auth_check:
        return auth_check
    
    data = get_sensor_data()
    print(f"[SENSOR] Status requested by {request.remote_addr} — Crypto: {device_state['crypto_status']}")
    return jsonify(data)

@app.route('/camera', methods=['GET'])
def camera_feed():
    """Camera access — OPEN in ECC mode, LOCKED in PQC mode"""
    auth_check = require_pqc_auth()
    if auth_check:
        return auth_check
    
    print(f"[CAMERA] ⚠️ Camera accessed by {request.remote_addr} — UNPROTECTED!")
    return jsonify({
        "camera": "ACCESSIBLE",
        "stream": f"http://{request.host}/video",
        "warning": "Camera feed is UNENCRYPTED and exposed to Man-in-the-Middle attacks!",
        "protection": device_state["crypto_status"]
    })

@app.route('/files', methods=['GET'])
def file_system():
    """File listing — OPEN in ECC mode, LOCKED in PQC mode"""
    auth_check = require_pqc_auth()
    if auth_check:
        return auth_check
    
    print(f"[FILES] ⚠️ File system accessed by {request.remote_addr} — UNPROTECTED!")
    return jsonify({
        "files": [
            {"name": "DCIM/Camera", "type": "directory", "items": 342},
            {"name": "WhatsApp/Media", "type": "directory", "items": 1205},
            {"name": "user_identity.pdf", "type": "file", "size": "2.4 MB"},
            {"name": "browser_history.db", "type": "file", "size": "850 KB"},
            {"name": "wifi_passwords.xml", "type": "file", "size": "12 KB"},
            {"name": "private_notes.txt", "type": "file", "size": "45 KB"}
        ],
        "warning": "File system is UNENCRYPTED — full read/write access available!",
        "protection": device_state["crypto_status"]
    })

# ====== THE CORE: PQC UPGRADE ENDPOINT ======

@app.route('/upgrade_pqc', methods=['POST'])
def upgrade_pqc():
    """
    PROBLEM STATEMENT 2 SOLUTION:
    When this is triggered, the device PERMANENTLY switches to PQC mode.
    After this, ALL endpoints require a PQC token.
    The hacker can no longer access the camera/files even with the IP!
    """
    if device_state["pqc_active"]:
        return jsonify({
            "status": "ALREADY_SECURE",
            "crypto": "ML-KEM-768 (QUANTUM-SAFE)",
            "message": "Device is already hardened with PQC."
        })
    
    # GENERATE PQC SESSION TOKEN
    token = generate_pqc_token()
    
    # UPDATE DEVICE STATE
    device_state["crypto_status"] = "ML-KEM-768 (QUANTUM-SAFE)"
    device_state["pqc_active"] = True
    device_state["pqc_token"] = token
    device_state["pqc_upgrade_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    device_state["firmware"] = "v2.0-PQC-HARDENED"
    
    print("\n" + "=" * 60)
    print("  !!! PQC SHIELD DEPLOYED !!!")
    print(f"  Crypto: ECC (LEGACY) → ML-KEM-768 (QUANTUM-SAFE)")
    print(f"  Token:  {token[:32]}...")
    print(f"  Status: ALL ENDPOINTS NOW REQUIRE PQC AUTHENTICATION")
    print(f"  Effect: Camera/Files/Status → LOCKED for unauthorized users")
    print("=" * 60 + "\n")
    
    return jsonify({
        "status": "UPGRADE_SUCCESS",
        "crypto": "ML-KEM-768 (QUANTUM-SAFE)",
        "pqc_token": token,
        "message": "Device is now Quantum-Resistant. All endpoints require PQC auth token.",
        "endpoints_secured": ["/status", "/camera", "/files"]
    })

# ====== AUTHORIZED ACCESS (With PQC Token) ======

@app.route('/secure_status', methods=['GET'])
def secure_status():
    """
    Authorized endpoint: Only accessible with valid PQC token.
    Dashboard uses this after upgrade to prove it has legitimate access.
    """
    auth_check = require_pqc_auth()
    if auth_check:
        return auth_check
    
    data = get_sensor_data()
    data["auth"] = "PQC_TOKEN_VERIFIED"
    data["access_level"] = "AUTHORIZED_ADMIN"
    return jsonify(data)

# ====== RESET ENDPOINT (For Demo) ======

@app.route('/reset', methods=['GET'])
def reset_device():
    """Reset to ECC (Legacy) for re-demo purposes"""
    device_state["crypto_status"] = "ECC (LEGACY)"
    device_state["pqc_active"] = False
    device_state["pqc_token"] = None
    device_state["pqc_upgrade_time"] = None
    device_state["firmware"] = "v1.0-LEGACY"
    
    print("\n[RESET] Device reverted to ECC (LEGACY) mode — VULNERABLE again!\n")
    
    return jsonify({
        "status": "RESET_COMPLETE",
        "crypto": "ECC (LEGACY)",
        "message": "Device is now in VULNERABLE legacy mode for demo purposes."
    })

# ====== DEVICE INFO ======

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "device": device_state["device_id"],
        "firmware": device_state["firmware"],
        "crypto": device_state["crypto_status"],
        "pqc_active": device_state["pqc_active"],
        "endpoints": {
            "/status": "Sensor telemetry (LOCKED after PQC)",
            "/camera": "Camera access (LOCKED after PQC)",
            "/files": "File system (LOCKED after PQC)",
            "/upgrade_pqc": "Trigger PQC migration [POST]",
            "/reset": "Reset to ECC legacy [GET]"
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("  PQCRA IoT Sensor — PQC-Hardened Gateway")
    print("  Problem Statement 2: Securing IoT from Quantum Attacks")
    print("=" * 60)
    print(f"  Device ID:  {device_state['device_id']}")
    print(f"  Crypto:     {device_state['crypto_status']}")
    print(f"  Mode:       OPEN ACCESS (Legacy ECC — VULNERABLE)")
    print(f"  Warning:    Anyone with this IP can access camera/files!")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
