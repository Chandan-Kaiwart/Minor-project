import urllib.request
import json
import time

# PQCRA Mission: RED-TEAM ATTACK DEMO
# This script simulates a Quantum Computer running Shor's Algorithm
# to crack the ECC encryption of the IoT Device.

TARGET_URL = "http://192.168.0.16:5000/status"

def simulate_quantum_crack():
    print("="*60)
    print("   QUANTUM ADVERSARY: INITIATING SHOR'S ATTACK (ECC-256)")
    print("="*60)
    
    try:
        # 1. INTERCEPT: Sniff the phone's legacy telemetry
        print(f"[SNIFF] Intercepting legacy ECC stream from {TARGET_URL}...")
        with urllib.request.urlopen(TARGET_URL, timeout=5) as response:
            encrypted_data = json.loads(response.read().decode())
            print(f"[DATA] Captured Metadata: {encrypted_data['id']} | Crypto: {encrypted_data['crypto_status']}")
            
            # 2. SHOR'S ALGORITHM (SIMULATED): Factoring the ECC Curve
            print("\n[QUANTUM] Solving Discrete Logarithm problem via 2048-Qubit Shor's Engine...")
            for i in range(10):
                time.sleep(0.3)
                print(f"[SHOR] Factoring Point P on Curve... {10*(i+1)}% complete")
            
            # 3. EXTRACTION: Proving the ECC layer is now transparent
            print("\n" + "!"*40)
            print("!!! SHOR'S ATTACK SUCCESSFUL: ECC CRACKED !!!")
            print("!"*40)
            print(f"EXTRACTED RAW TELEMETRY (Private Data Exposed):")
            print(f" > TEMP: {encrypted_data['temperature']}C")
            print(f" > BATT: {encrypted_data['battery']}%")
            print(f" > SIGNAL: {encrypted_data['signal_strength']} dBm")
            print("!"*40)
            
    except Exception as e:
        print(f"[ATTACK FAILED] Target unreachable or already PQC-Secured: {e}")

if __name__ == "__main__":
    simulate_quantum_crack()
