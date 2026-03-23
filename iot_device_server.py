"""
IoT Device Server — Run this on your Android phone via Termux:
  pip install flask flask-cors requests
  python iot_device_server.py

This script simulates an ECC-vulnerable IoT device that gets upgraded to ML-KEM.
Ensure IPWebcam is actively streaming live camera at http://127.0.0.1:8080 on the phone.
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import hashlib, random, time, os, json
import requests

app = Flask(__name__)
CORS(app)  # Allow dashboard to call device directly

STATE_FILE = "device_security_state.json"

def load_state():
    """Loads device security state from a local file, ensuring persistence across reloads."""
    default_state = {
        "crypto_status": "ECC (LEGACY)",
        "threat_level": "HIGH",
        "secured": False
    }
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                saved_data = json.load(f)
                default_state.update(saved_data)
        except Exception:
            pass
    return default_state

def save_state():
    """Saves device security state to a local file."""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(device_state, f, indent=4)
    except Exception as e:
        print(f"[ERROR] Failed to save state to {STATE_FILE}: {e}")

# Global state that loads when the Termux script starts
device_state = load_state()

# Simulated files accessible when ECC is broken
EXPOSED_FILES = [
    "identity_proof.jpg",
    "wifi_passwords.txt",
    "whatsapp_db.crypt12"
]

@app.route('/status', methods=['GET'])
def status():
    """Returns current device crypto status."""
    return jsonify({
        "crypto_status": device_state["crypto_status"],
        "threat_level": device_state["threat_level"],
        "secured": device_state["secured"],
        "temperature": round(random.uniform(28.5, 38.5), 1),
        "battery": random.randint(45, 92),
        "cpu": random.randint(18, 67),
        "signal": random.randint(-85, -55)
    })

@app.route('/exploit', methods=['GET'])
def exploit():
    """
    BREACH endpoint — only accessible when device uses ECC (LEGACY).
    If PQC is implemented, it blocks the exploit natively.
    """
    if device_state["secured"]:
        return jsonify({
            "error": "ACCESS_DENIED",
            "reason": "PQC-SHIELD ACTIVE — ML-KEM Authentication Required",
            "http_code": 403
        }), 403

    fake_key_bytes = hashlib.sha256(b"ecc_secp256k1_private").hexdigest()
    
    # ⚠️ This exact print statement was requested by your dashboard logs!
    print(f"\n[!!!] ATTACK from {request.remote_addr} - ECC key exposed!")
    
    return jsonify({
        "status": "BREACH_SUCCESS",
        "intercepted_key": f"dA=0x{fake_key_bytes[:16]}... (secp256k1)",
        "exposed_files": EXPOSED_FILES,
        "camera_accessible": True
    })

@app.route('/upgrade_pqc', methods=['POST', 'OPTIONS'])
def upgrade_pqc():
    """
    IMPLEMENT SECURITY endpoint — AI dashboard pushes ML-KEM config here to secure the device.
    """
    if request.method == 'OPTIONS':
        return '', 204

    # ⚠️ This exact print statement was requested by your dashboard logs!
    print("\n" + "#"*41)
    print("!!! PQC SHIELD DEPLOYMENT INITIATED !!!")
    print("STATUS: DEVICE SECURED")
    print("#"*41 + "\n")

    # Transition device state to Secure
    device_state["crypto_status"] = "ML-KEM (QUANTUM-SAFE)"
    device_state["threat_level"]  = "LOW"
    device_state["secured"]       = True
    save_state()

    return jsonify({
        "status": "SUCCESS",
        "result": "ML-KEM-768 deployed — Device is now QUANTUM-SAFE",
        "pqc_token": "PQC-" + hashlib.sha256(str(time.time()).encode()).hexdigest()[:16].upper()
    })

@app.route('/camera')
def camera_snapshot():
    """
    Device-side Camera Enforcement point.
    If the device is secured, the firewall BLOCKS the video stream at the edge.
    If unsecured, it proxies IPWebcam snapshot (127.0.0.1:8080/shot.jpg).
    """
    if device_state["secured"]:
        # Block access completely if secured!
        return "BLOCKED BY PQC SHIELD — ML-KEM Authentication Required", 403
        
    try:
        # Fetch the actual camera image from the IPWebcam app on the phone
        r = requests.get('http://127.0.0.1:8080/shot.jpg', timeout=3)
        return Response(r.content, mimetype='image/jpeg')
    except Exception as e:
        return f"Camera Offline: Is IPWebcam running on port 8080? {e}", 500

@app.route('/reset', methods=['POST'])
def reset():
    """Simulates a physical USB flash. Reverts security back to vulnerable ECC."""
    device_state["crypto_status"] = "ECC (LEGACY)"
    device_state["threat_level"]  = "HIGH"
    device_state["secured"]       = False
    save_state()
    return jsonify({"status": "RESET", "message": "Device reverted to ECC via Simulated USB"})

if __name__ == '__main__':
    print("=" * 60)
    print("  IoT DEVICE SECURE EDGE SERVER — RUNNING ON TERMUX")
    print("=" * 60)
    print("  Ensure IPWebcam is running on port 8080 in the background.")
    app.run(host='0.0.0.0', port=5000, debug=False)
