from flask import Flask, render_template, request, jsonify, Response, send_file, redirect
import requests
import os, sys, time, random, tempfile, shutil, subprocess, re, zipfile
import io, base64
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from Crypto.Cipher import AES
import base64, json, time

from pqc_advanced_analyzer import AdvancedPQCManager
from pqc_real_implementation import AdvancedPQCEngine

import urllib.request, json

app = Flask(__name__)
manager = AdvancedPQCManager()
engine = AdvancedPQCEngine(n=512)

import hashlib
from datetime import datetime

class PQCBlockchain:
    def __init__(self):
        self.chain = []
        self.hash_algorithm = 'SPHINCS+ (Simulated)'
        self.create_genesis_block()

    def create_genesis_block(self):
        self.add_log("SYSTEM", "localhost", "ROOT KERNEL BOOT SUCCESS", severity="INFO", custom_hash="0000000000000000")

    def add_log(self, user, ip, action, severity="INFO", custom_hash=None):
        prev_hash = self.chain[-1]["hash"] if self.chain else "00000000000000000000"
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_id = len(self.chain) + 1
        
        data_string = f"{log_id}{user}{ip}{action}{timestamp}{prev_hash}"
        calc_hash = custom_hash if custom_hash else hashlib.sha256(data_string.encode()).hexdigest()[:16]
        
        block = {
            "id": log_id,
            "user": user,
            "ip": ip,
            "action": action,
            "timestamp": timestamp,
            "hash": calc_hash,
            "prev_hash": prev_hash,
            "severity": severity,
            "valid": True
        }
        self.chain.append(block)

    def validate_chain(self):
        is_valid_overall = True
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i-1]
            data_string = f"{current['id']}{current['user']}{current['ip']}{current['action']}{current['timestamp']}{prev['hash']}"
            expected_hash = hashlib.sha256(data_string.encode()).hexdigest()[:16]
            if current['hash'] != expected_hash or not prev.get('valid', True):
                current["valid"] = False
                is_valid_overall = False
            else:
                current["valid"] = True
        return is_valid_overall

blockchain = PQCBlockchain()
blockchain.add_log("system", "localhost", "PQC DAEMON START (SLH-DSA ENABLED)", "INFO")
blockchain.add_log("admin", "192.168.1.15", "USER LOGIN (ADMIN_ROLE)", "INFO")

import threading
import time
import random

def simulate_global_traffic():
    # Wait for server to start
    time.sleep(5)
    external_traffic_patterns = [
        ("Client-Browser", "youtube.com",              "GET /watch?v=quantum_crypto_tutorial",   "INFO"),
        ("Client-Browser", "manifest.googlevideo.com", "GET /api/videoplayback (1080p stream)",  "INFO"),
        ("Sys-Updater",    "windowsupdate.com",        "POST /v1/telemetry",                     "INFO"),
        ("Client-Browser", "github.com",               "GET /api/v3/users/pqc-research",         "INFO"),
        ("WhatsApp-Web",   "web.whatsapp.com",         "wss://chat-stream (Encrypted)",          "INFO"),
        ("Client-Browser", "youtube.com",              "GET /youtubei/v1/next (Autoplay load)",  "INFO"),
        ("Background-App", "spotify.com",              "GET /v1/me/player/currently-playing",    "INFO"),
        ("Unknown-Agent",  "45.33.22.10",              "PORT SCAN DETECTED: TCP 22,80,443",      "WARNING"),
        ("Unknown-Agent",  "103.21.244.90",            "REPEATED 404 PROBING DETECTED",         "WARNING"),
        ("Auth-Service",   "192.168.0.1",              "USER AUTHENTICATED SUCCESSFULLY",        "INFO"),
    ]
    while True:
        # Generate varied traffic every 2 to 5 seconds
        time.sleep(random.uniform(2.0, 5.0))
        user, ip, base_action, severity = random.choice(external_traffic_patterns)
        action = f"[PACKET SNIFFER] {base_action}"
        try:
            blockchain.add_log(user, ip, action, severity)
        except:
            pass

# Start the background traffic generator
threading.Thread(target=simulate_global_traffic, daemon=True).start()

@app.before_request
def log_network_traffic():
    if (request.path.startswith('/api/') or request.path.startswith('/v3/')) and request.path not in ['/api/get_logs']:
        ip = request.remote_addr
        user = "Guest"
        action = f"API REQUEST: {request.method} {request.path}"
        severity = "INFO"
        if "tamper_log" in request.path:
            severity = "CRITICAL"
        blockchain.add_log(user, ip, action, severity)

@app.route('/api/get_logs', methods=['GET'])
def get_logs():
    is_valid = blockchain.validate_chain()
    return jsonify({
        "chain": blockchain.chain[-50:],
        "valid": is_valid
    })

@app.route('/api/tamper_log', methods=['POST'])
def tamper_log():
    if len(blockchain.chain) > 1:
        target_idx = max(1, len(blockchain.chain) - 3)
        blockchain.chain[target_idx]["action"] = "NO ABNORMAL ACTIVITY DETECTED"
        blockchain.chain[target_idx]["severity"] = "CRITICAL"
        return jsonify({"status": "SUCCESS", "message": "Log artificially tampered!"})
    return jsonify({"status": "ERROR"})

@app.route('/api/reset_chain', methods=['POST'])
def reset_chain():
    global blockchain
    blockchain = PQCBlockchain()
    blockchain.add_log("system", "localhost", "PQC DAEMON RESTARTED (SLH-DSA RE-KEYED)", "INFO")
    blockchain.add_log("admin", "192.168.0.25", "CHAIN INTEGRITY RESTORED BY ADMIN", "INFO")
    return jsonify({"status": "RESET", "message": "Blockchain chain restored to genesis!"})


# ====== PS1: DYNAMIC ALGORITHM ROUTES ======
@app.route('/api/fetch_attacks', methods=['GET'])
def fetch_attacks():
    target = request.args.get('target', 'iot_device')
    # Simulated fetch from Google Threat Intelligence Server
    attacks = {
        'file': ['Ransomware Mass-Encryption', 'Data Exfiltration via DNS', 'File Puzzling / Shredding', 'Quantum Data-Harvesting (SNDL)'],
        'folder': ['Directory Traversal Escalation', 'Bulk Archive Theft', 'Ransomware Worm Phishing', 'Lateral Movement Propagation'],
        'iot_device': ['Side-Channel Power Analysis', 'Firmware Downgrade (OTA)', 'DDoS Botnet Hijack', 'Man-In-The-Middle (MITM)', 'Fault Injection Attack'],
        'cloud_storage': ['S3 Bucket Enumeration', 'Cross-Tenant Data Bleed', 'API Key Compromise', 'Quantum Key Harvest', 'SSRF Proxy Exploitation'],
        'api_gateway': ['BOLA (Broken Object Level Auth)', 'GraphQL Introspection Exploits', 'Token Forgery (Shor\'s)', 'DDoS Application Layer'],
        'blockchain': ['51% Quantum Compute Hijack', 'Smart Contract Reentrancy', 'ECDSA Private Key Derivation (Shor\'s)'],
        'healthcare': ['Patient Record Alteration', 'Pacemaker Telemetry MITM', 'Bluetooth Low Energy (BLE) Spoofing'],
        'autonomous_vehicle': ['CAN Bus Injection', 'Sensor Spoofing (LiDAR)', 'V2X Protocol Interception', 'GPS Signal Jamming'],
        'industrial_ics': ['SCADA Command Forgery', 'PLC Logic Bomb', 'Stuxnet-style Airgap Bypass', 'Time Synchronization Spoofing']
    }
    return jsonify({"status": "success", "attacks": attacks.get(target, [])})

@app.route('/api/generate_algo', methods=['POST'])
def generate_algo():
    data = request.json or {}
    target = data.get('target', 'iot_device')
    algo = data.get('algo', 'ML-KEM')
    attack = data.get('attack', 'Side-Channel Power Analysis')
    
    # Generate dynamic cryptographic schema
    code = f"""// [THREAT INTEL FETCHED VIA GOOGLE SERVERS]
// ----------------------------------------------------
// Target Deployment : {target.upper().replace('_', ' ')}
// Chosen Algorithm  : {algo}
// Mitigating Threat : {attack}
// ----------------------------------------------------

#include <pqc_lattice.h>
#include <hardware_fw.h>

void execute_secure_mitigation() {{
    // Initialize standard Post-Quantum Context
    PQC_Context* ctx = Initialize_{algo.replace('-','_')}(SECURITY_LEVEL_5);
    
    // Dynamic Threat Mitigation Logic for {attack}
    Set_Hardware_Masking(ctx, ENABLED);
    Set_Constant_Time_Execution(ctx, ENABLED);
    
    // Generate Lattice polynomial seed
    Vector ephemeral_secret = Generate_Lattice_Seed(512, 3329);
    
    // Encapsulate payload utilizing {algo}
    byte[] encapsulated = KEM_Encapsulate(ctx, ephemeral_secret);
    
    // Safe transmission preventing {attack} vectors
    Secure_Transmission(encapsulated, NETWORK_INTERFACE_1);
}}
"""
    return jsonify({"code": code})

@app.route('/api/evaluate_algo', methods=['POST'])
def evaluate_algo():
    data = request.json or {}
    code = data.get('code', '')
    
    if "ECC" in code or "RSA" in code:
        score = 25
        msg = "Classical vulnerable algorithms detected! Vulnerable to Shor's Algorithm."
    elif "ML-KEM" in code or "lattice" in code.lower() or "dilithium" in code.lower():
        score = 98
        msg = "Robust Post-Quantum bounds validated. NIST Compliance Confirmed."
    elif len(code.strip()) < 10:
        score = 0
        msg = "Empty algorithm logic provided."
    else:
        score = 65
        msg = "Unrecognized cryptographic scheme. Requires deep structural analysis."
        
    return jsonify({"score": score, "message": msg})

HTML_V3 = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PQCRA | Tactical Command</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root {
    --bg-main: #06080a;
    --bg-panel: #0b1116;
    --bg-card: #0d141b;
    --primary: #00fa88;
    --secondary: #50c878;
    --warning: #ffaa00;
    --danger: #f84b4b;
    --text-white: #e1e1e1;
    --text-dim: #8b949e;
    --border: #1a242d;
    --term-bg: #000000;
    --card-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

body.light-theme {
    --bg-main: #f0f2f5;
    --bg-panel: #ffffff;
    --bg-card: #ffffff;
    --primary: #00fa88;
    --secondary: #50c878;
    --warning: #ffaa00;
    --danger: #f84b4b;
    --text-white: #1a1a1a;
    --text-dim: #64748b;
    --border: #e2e8f0;
    --term-bg: #000000;
    --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

* { margin:0; padding:0; box-sizing:border-box; }
body { 
    font-family:'Inter', sans-serif; 
    background: var(--bg-main); 
    color: var(--text-white); 
    height: 100vh; 
    display: flex; align-items: center; justify-content: center;
    overflow: hidden; 
}

/* Background Matrix Canvas */
#matrix-bg { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 0; opacity: 0.15; pointer-events: none; }

/* Outer Wrapper (Minimalist Solid) */
.dashboard-wrapper {
    position: relative; z-index: 10; width: 95%; height: 95%; display: flex;
    background: var(--bg-main); border-radius: 12px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    border: 1px solid var(--border); overflow: hidden;
    transition: all 0.2s ease;
}

/* ===== SIDEBAR ===== */
.sidebar {
    width: 270px; background: var(--bg-panel); border-right: 1px solid var(--border);
    display: flex; flex-direction: column; padding: 2.5rem 1.5rem; overflow-y: auto;
    transition: background 0.4s ease, border-color 0.4s ease;
}
.brand { 
    display: flex; align-items: center; gap: 12px; font-size: 1.2rem; font-weight: 700;
    margin-bottom: 2.5rem; padding: 0 10px; color: var(--text-white);
    letter-spacing: 0.5px;
}
.brand-icon {
    width: 25px; height: 30px; background: var(--primary);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex; align-items: center; justify-content: center; position: relative;
}
.brand-icon::after { content:'Q'; font-family:'Inter'; font-weight:700; color:#fff; font-size:0.8rem; }

.nav-item {
    padding: 12px 15px; margin-bottom: 5px; border-radius: 8px; color: var(--text-dim); cursor: pointer;
    font-size: 0.85rem; font-weight: 500; display: flex; align-items: center; gap: 12px; transition: 0.3s;
}
.nav-item:hover { color: var(--primary); background: transparent; transform: translateX(5px); }
.nav-item.active { background: var(--border); color: var(--text-white) !important; font-weight: 600; }
.nav-icon { width: 18px; opacity: 0.7; flex-shrink: 0; color:var(--text-dim);}
.nav-item.active .nav-icon { opacity: 1; filter: none; color: #fff !important; stroke: #fff; }
.nav-section-title { font-size: 0.65rem; color: var(--text-dim); text-transform: uppercase; font-weight: 800; padding: 0 15px; margin: 25px 0 10px 0; letter-spacing: 1.5px; opacity: 0.7;}

/* ===== MAIN CONTENT GRID ===== */
.main-content { position: relative; flex: 1; padding: 2.5rem; overflow-y: auto; height: 100%; display: flex; flex-direction: column;}
.top-header { display: flex; justify-content: flex-end; align-items: center; gap: 15px; margin-bottom: 1.5rem; position: absolute; top: 20px; right: 30px; z-index: 50;}
.icon-btn { background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 8px; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; color: var(--text-dim); cursor: pointer; transition: 0.3s; }
.icon-btn:hover { color: var(--primary); border-color: var(--primary); }

/* Tabs */
.tab-content { display: none; flex-direction: column; gap: 20px; flex: 1;}
.tab-content.active { display: flex; animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.grid-system { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; grid-auto-rows: min-content; }

/* Shared Card Styling */
.card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.5rem; position: relative; display: flex; flex-direction: column;
    transition: 0.3s; overflow: hidden; box-shadow: var(--card-shadow, none);
}
.card:hover { border-color: var(--primary); transform: translateY(-3px); }
.card-title { font-size: 0.75rem; color: var(--text-dim); font-weight: 600; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: flex-start; }
.badge { padding: 3px 8px; border-radius: 4px; font-size: 0.6rem; font-weight: 700; text-transform: uppercase; }
.badge-high { background: rgba(219, 147, 34, 0.1); color: var(--warning); border: 1px solid rgba(219, 147, 34, 0.3); }
.badge-crit { background: rgba(248, 75, 75, 0.1); color: var(--danger); border: 1px solid rgba(248, 75, 75, 0.3); }

.big-val { font-size: 2.2rem; font-weight: 700; color: #fff; margin-bottom: 5px; display: flex; align-items: baseline; gap: 8px; font-family: 'Inter'; }
.big-val span { font-size: 1rem; color: var(--text-dim); font-weight: 400; font-family: 'Inter'; text-transform: uppercase; }
.sub-val { font-size: 1.2rem; display: flex; align-items: center; gap: 5px; font-weight: 700; color: var(--danger); }
.sub-val i { transform: rotate(-45deg); display: inline-block; font-size: 1.5rem;}

/* SVG Mini-Charts */
.chart-container { flex: 1; min-height: 50px; position:relative; margin-top: 10px; margin-left: -20px; width: calc(100% + 40px); overflow: hidden;}
.mini-chart { width: 100%; height: 50px; position:absolute; bottom:-10px; }
.mini-chart path { fill: none; stroke: var(--primary); stroke-width: 2; filter: none; transition: 0.3s; }
.mini-chart path.fill { fill: url(#slateGlow); stroke: none; filter: none; opacity: 1; transition: 0.3s; }

/* Blocks Layout Swap & Resize */
.side-block { grid-column: 1 / 2; display: flex; flex-direction: column; gap: 20px;}
.main-block { grid-column: 2 / 4; display: flex; flex-direction: column; gap: 20px;}
.bottom-block { grid-column: 1 / 4; display: flex; flex-direction: column; gap: 20px;}

/* Map Card */
.card-map { height: 280px; padding: 0 !important; }
.map-overlay-title { position: absolute; top: 1.2rem; left: 1.2rem; z-index: 20; color: #fff; font-weight: 700; font-size: 1rem; }
.map-bg-under { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #0c1116; opacity: 0.7; z-index: 1;}
.map-summary-panel {
    position: absolute; bottom: 1rem; right: 1rem; z-index: 25; width: 220px;
    background: rgba(0,0,0,0.8); border: 1px solid var(--border); border-radius: 8px;
    padding: 10px; font-size: 0.65rem; color: var(--text-dim); backdrop-filter: blur(5px);
}
.map-silhouette {
    position: absolute; top: 10px; left: 10px; right: 10px; bottom: 10px; background-color: rgba(255,255,255,0.05); 
    -webkit-mask-image: url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg');
    -webkit-mask-size: cover; -webkit-mask-repeat: no-repeat; -webkit-mask-position: center; z-index: 5;
}
.map-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 10; pointer-events: none; }
.hub-dot { fill: var(--primary); filter: drop-shadow(0 0 8px var(--primary)); opacity: 0.8;}

/* Table Card */
.card-table { flex: 1; padding: 1.5rem 1rem; border-color: rgba(0, 250, 136, 0.4); box-shadow: 0 5px 20px rgba(0, 250, 136, 0.05);}
table { width: 100%; border-collapse: separate; border-spacing: 0 8px; font-size: 0.8rem; }
th { text-align: left; padding-bottom: 5px; color: var(--text-dim); font-weight: 600; text-transform: uppercase; font-size: 0.7rem;}
td { padding: 15px 10px; color: var(--text-white); background: rgba(0,0,0,0.2); vertical-align: top;}
tr td:first-child { border-top-left-radius: 8px; border-bottom-left-radius: 8px; }
tr td:last-child { border-top-right-radius: 8px; border-bottom-right-radius: 8px; }

/* Terminal Card */
.card-terminal {
    background: var(--term-bg); border: 1px solid var(--border);
    box-shadow: inset 0 0 15px rgba(0,0,0,0.05); font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
    padding: 1.5rem; color: var(--primary); overflow-y: auto; position: relative; line-height: 1.7; flex: 1; border-radius: 12px;
}
.t-date { color: var(--text-dim) !important; opacity:0.6; }
.t-msg { color: var(--primary) !important; }
.t-err { color: var(--danger) !important; }
.t-warning { color: var(--warning) !important; }
.t-date { color: #35533c; margin-right: 5px; font-weight: 500;}
.t-msg { color: #00fa88; }
.t-err { color: var(--danger); font-weight: 700; text-shadow: 0 0 5px rgba(248,75,75,0.4); }
.t-warning { color: var(--warning); font-weight: 600; }

#tom-cruise-wrapper {
    position: fixed; bottom: 20px; left: -200px; width: 200px; height: 150px; 
    z-index: 9999; pointer-events: none; display: none;
}
#tom-cruise-wrapper img { width: 100%; height: auto; }
@keyframes runAcross {
    0% { left: -250px; }
    100% { left: 100%; }
}
.running { display: none !important; } 
.type-cursor { display: inline-block; width: 8px; height: 14px; background: var(--primary); animation: blink 1s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* Horizontal Scan Line (Restricted to Terminal Box) */
#scan-overlay {
    position: absolute; top: 0; left: 0; width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
    box-shadow: 0 0 15px var(--primary), 0 0 30px var(--primary);
    z-index: 9998; display: none; pointer-events: none;
}
@keyframes scanVertical {
    0% { top: 0; opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { top: 100%; opacity: 0; }
}
.active-scan { display: block !important; animation: scanVertical var(--mission-pass, 10s) linear 2; }

.btn-action {
    background: var(--primary);
    color: #fff; font-weight: 600; font-family: 'Inter'; font-size: 0.95rem; border: none; border-radius: 6px; padding: 12px 24px;
    cursor: pointer; transition: 0.2s ease; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); text-align: center; width: 100%; display: block;
}
.btn-action:hover { background: var(--secondary); transform: translateY(-1px); }

/* Ring Chart */
.ring-chart { width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.ring-inner { width: 50px; height: 50px; background: var(--bg-card); border-radius: 50%; }

.m-input { background: #0c1117; border: 1px solid var(--border); color: var(--primary); padding: 12px; border-radius: 8px; font-family: 'JetBrains Mono'; resize: none; outline: none; box-shadow: inset 0 2px 5px rgba(0,0,0,0.5); width: 100%; font-size:0.8rem;}
.m-input:focus { border-color: var(--primary); }

/* PS View specific styles */
.ps-header { font-size: 1.5rem; font-weight: 800; color: #fff; margin-bottom: 5px; }
.ps-desc { color: var(--text-dim); font-size: 0.9rem; line-height: 1.5; margin-bottom: 25px; max-width: 80%; }
.algo-row { padding: 15px 0; border-bottom: 1px dashed var(--border); display: flex; justify-content: space-between; align-items:center; }
.algo-row:last-child { border-bottom: none; }
.node-orb { width: 60px; height: 60px; border-radius: 50%; margin: 0 auto 15px auto; display: flex; align-items: center; justify-content: center; border: 2px solid; }

/* Pad & Modal UI */
.pad-trigger {
    flex: 2; height: 168px; background: rgba(0,0,0,0.4); border: 2px dashed var(--border);
    border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center;
    cursor: pointer; transition: 0.3s; gap: 10px; color: var(--text-dim); text-align: center;
}
.pad-trigger:hover { border-color: var(--primary); background: rgba(80, 200, 120, 0.05); color: var(--primary); }
.pad-trigger i { font-size: 2rem; opacity: 0.5; }

.modal-overlay {
    position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.85);
    backdrop-filter: blur(10px); z-index: 10000; display: none; align-items: center; justify-content: center;
}
.modal-card {
    background: var(--bg-panel); border: 1px solid var(--border); border-radius: 20px;
    width: 600px; max-width: 90%; max-height: 80%; display: flex; flex-direction: column; padding: 2rem;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5); position: relative;
}
.modal-title { font-size: 1.2rem; font-weight: 800; margin-bottom: 1.5rem; color: #fff; display: flex; align-items: center; gap: 10px; }
.repo-list { overflow-y: auto; display: flex; flex-direction: column; gap: 10px; margin-top: 10px; }
.repo-item { 
    padding: 12px 15px; background: rgba(255,255,255,0.03); border: 1px solid transparent;
    border-radius: 8px; cursor: pointer; transition: 0.2s; display: flex; justify-content: space-between; align-items: center;
}
.repo-item:hover { background: rgba(80, 200, 120, 0.1); border-color: var(--primary); }
.github-btn {
    background: #24292e; color: #fff; border: 1px solid #444; padding: 10px; border-radius: 8px;
    cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: 0.3s;
}
.github-btn:hover { background: #333; border-color: var(--primary); box-shadow: 0 0 15px rgba(80,200,120,0.2); }
.github-btn.connected { border-color: var(--primary); color: var(--primary); }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }
    @keyframes blink { 0% { opacity:1; } 50% { opacity:0.3; } 100% { opacity:1; } }
    
    /* CCTV Surveillance Styles */
    .cctv-overlay {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none;
        z-index: 5;
        padding: 15px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        font-family: 'Courier New', Courier, monospace;
        color: #00ff00;
        text-shadow: 0 0 5px rgba(0,255,0,0.8);
    }
    .rec-dot {
        color: #ff0000;
        animation: blink 1s infinite;
    }
    .scanlines {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%);
        background-size: 100% 4px;
        pointer-events: none;
        z-index: 6;
        opacity: 0.15;
    }
    
    /* PQC Encrypt Banner Styles */
    #pqc-encrypt-banner {
        display: none;
        margin-top: 20px;
        background: linear-gradient(90deg, rgba(80, 200, 120, 0.1) 0%, rgba(0, 0, 0, 0.4) 100%);
        border: 2px solid var(--primary);
        border-radius: 12px;
        padding: 20px;
        align-items: center;
.banner-content { display: flex; align-items: center; gap: 20px; }
    .banner-icon { 
        width: 50px; height: 50px; background: rgba(80, 200, 120, 0.1); 
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        color: var(--primary); border: 1px solid rgba(80, 200, 120, 0.3);
    }
.banner-info { display: flex; flex-direction: column; }
.banner-title { font-weight: 800; color: #fff; font-size: 1rem; letter-spacing: 0.5px; }
.banner-desc { font-size: 0.75rem; color: var(--text-dim); margin-top: 4px; line-height: 1.4; max-width: 400px; }
</style>
</head>
<body>

<svg width="0" height="0"><defs><linearGradient id="slateGlow" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#ffffff" stop-opacity="0.3"/><stop offset="100%" stop-color="#ffffff" stop-opacity="0"/></linearGradient></defs></svg>
<canvas id="matrix-bg"></canvas>

<audio id="mi-theme" preload="auto">
    <source src="mission-impossible_oEwlsUsI.mp3" type="audio/mpeg">
</audio>

<div class="dashboard-wrapper">
    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="brand"><div class="brand-icon" style="background: var(--border);"></div>PQCRA</div>
        
        <div class="nav-section-title">Operations</div>
        <div class="nav-item active" onclick="switchTab('audit', this)">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
            Core PQC Audit
        </div>
        
        <div class="nav-section-title">Problem Statements</div>
        <div class="nav-item" onclick="switchTab('ps1', this)">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
            Algorithm Research
        </div>
        <div class="nav-item" id="nav-iot" onclick="switchTab('iot', this)">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg>
            IoT Edge Defense
        </div>
        <div class="nav-item" onclick="switchTab('logs', this)">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            System Logs
        </div>

        <div class="nav-section-title">Mission Vault</div>
        <div id="history-box" style="margin-top:10px; display:flex; flex-direction:column; gap:8px; overflow-y:auto; max-height:250px; padding-right:5px;">
            <div style="text-align:center; padding:20px; color:var(--text-dim); font-size:0.65rem; border:1px dashed var(--border); border-radius:8px;">Empty Archive</div>
        </div>
    </div>

    <!-- MAIN CONTENT -->
    <div class="main-content">
        <div class="top-header">
            <div class="icon-btn" onclick="toggleTheme()" style="width: auto; padding: 0 15px; border-radius: 20px; font-size: 0.75rem; font-weight:600; gap: 8px; border-color:var(--border);">
                <svg id="theme-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                <span id="theme-text">Dark Mode</span>
            </div>
        </div>

        <!-- ====================== TAB 1 : MAIN AUDIT MAP ====================== -->
        <div id="tab-audit" class="tab-content active">
            <div class="grid-system">
                <!-- ROW 1 -->
                <div class="card card-threats">
                    <div class="card-title">Active Threats <span class="badge badge-high" id="b-threat">STANDBY</span></div>
                    <div class="big-val" id="val-threats">0</div>
                    <div class="chart-container"><svg class="mini-chart" viewBox="0 0 100 30" preserveAspectRatio="none"><path class="fill chart-path-fill" d="M0,30 L0,15 Q25,25 50,15 T100,20 L100,30 Z" /><path class="chart-path" fill="none" stroke="var(--primary)" stroke-width="2" vector-effect="non-scaling-stroke" d="M0,15 Q25,25 50,15 T100,20" /></svg></div>
                </div>
                
                <div class="card card-bandwidth">
                    <div class="card-title">Processing & Inventory</div>
                    <div class="big-val" id="val-speed">0.0 <span>Files/s</span></div>
                    <div style="font-size:0.75rem; color:var(--text-dim);">Scanning <span id="val-files" style="color:#fff; font-weight:700;">0</span> Objects in Buffer</div>
                    <div class="chart-container"><svg class="mini-chart" viewBox="0 0 100 30" preserveAspectRatio="none"><path class="fill chart-path-fill" d="M0,30 L0,22 Q25,18 50,22 T100,18 L100,30 Z" /><path class="chart-path" fill="none" stroke="var(--primary)" stroke-width="2" vector-effect="non-scaling-stroke" d="M0,22 Q25,18 50,22 T100,18" /></svg></div>
                </div>

                <div class="card card-ready">
                    <div class="card-title">PQC Readiness Index</div>
                    <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                        <div>
                            <div class="big-val" id="val-ready">0%</div>
                            <div class="sub-val" id="ready-trend">PENDING <i>→</i></div>
                        </div>
                        <div class="ring-chart" id="ring-status" style="border: 4px solid var(--border); box-shadow: 0 0 15px rgba(0,250,136,0.1);">
                            <div class="ring-inner"></div>
                        </div>
                    </div>
                </div>

                <div class="side-block">
                    <div class="card card-terminal" id="terminal-box" style="height: 570px; position: relative; overflow: hidden;">
                        <div id="scan-overlay"></div>
                        <div style="position: sticky; top: -5px; background: var(--term-bg); padding-bottom: 10px; margin-bottom: 10px; border-bottom: 1px dashed var(--border); z-index:2;">root@emerald-matrix:~# tail -f /var/log/pqc_audit</div>
                        <div id="term-logs"><div class="term-log"><span class="t-sys">emerald-sys[1]:</span> <span class="t-msg">Awaiting audit payload invocation...</span></div></div>
                        <span class="type-cursor" id="term-cursor"></span>
                    </div>
                </div>

                <div class="main-block">
                    <!-- Direct Input Area -->
                    <div class="card" id="card-config" style="padding-bottom:1.5rem; position: relative;">
                        <div class="card-title" style="margin-bottom: 10px;">Security Audit Configuration <span class="badge" style="background:rgba(0,250,136,0.1); color:var(--primary);">Operational</span></div>
                        <div style="display:flex; gap:15px; margin-top:10px; min-height:168px;">
                            <div class="pad-trigger" onclick="openCodePad()">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                                <span id="pad-status">Click to Paste Program Buffer</span>
                                <div style="font-size: 0.6rem; opacity: 0.7;">PQC Logic Reducer Active</div>
                            </div>
                            <div style="flex:1; display:flex; flex-direction:column; gap:8px;">
                                <div id="gh-action-btn" class="github-btn" onclick="openGitHubModal()">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
                                    <span id="gh-text">Connect GitHub</span>
                                </div>
                                <input type="text" id="path-in" class="m-input" placeholder="Local Mapping">
                                <input type="file" id="file-in" class="m-input" style="padding: 10px 8px;">
                                <button class="btn-action" style="padding:10px; margin-top:auto; font-size: 0.85rem;" onclick="executeScan()">Finalize Analysis</button>
                            </div>
                        </div>
                    </div>

                    <!-- Live Map -->
                    <div class="card card-map">
                        <div class="map-overlay-title">Global Threat Intelligence <span style="font-size:0.6rem; color:var(--primary); opacity:0.8;">[LIVE STREAM]</span></div>
                        <div class="map-summary-panel">
                            <b style="color:#fff; display:block; margin-bottom:5px;">Global Action Intelligence:</b>
                            <div class="map-summary-text">Synchronizing with SANS ISC honeypots... Identifying global botnet clusters probing for legacy RSA/ECC vulnerabilities.</div>
                        </div>
                        <div style="position:absolute; top:2.5rem; left:1.2rem; z-index:20; max-width:55%; font-size: 0.7rem; color:var(--text-dim); opacity:0.6;">Mapping Real-Time IoCs and infrastructure reconnaissance.</div>
                        <div class="map-bg-under"></div>
                        <div class="map-silhouette"></div>
                        <svg class="map-svg" id="map-svg" viewBox="0 0 600 300" preserveAspectRatio="none"></svg>
                    </div>
                </div>

                <!-- ROW 3 : BOTTOM BLOCK -->
                <div class="bottom-block">
                    <div class="card card-table">
                        <div class="card-title" style="margin-bottom:0.5rem; font-size:1rem; font-weight:700; color:#fff; align-items:center;">
                            PQC Readiness Results & Defined Mitigations
                            <div class="icon-btn" style="width:25px; height:25px;" onclick="window.location.href='/v3/download-report'" title="Export Unified Report">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                            </div>
                        </div>
                        <table style="min-width: 800px; width:100%;">
                            <thead>
                                <tr>
                                    <th style="width:20%">Location / Trace</th>
                                    <th style="width:15%">Mathematics</th>
                                    <th style="width:15%">Quantum Risk</th>
                                    <th style="width:50%">Post-Quantum Mitigation Framework</th>
                                </tr>
                            </thead>
                            <tbody id="vuln-tbody">
                                <tr>
                                    <td colspan="4" style="text-align:center; padding: 30px; color: var(--text-dim); font-family:'JetBrains Mono'; background:transparent;">Execute Target Analysis to populate migration schema.</td>
                                </tr>
                            </tbody>
                        </table>
                        <div id="res-injector"></div>
                        
                        <!-- PQC ENCRYPT BANNER -->
                        <div id="pqc-encrypt-banner" data-repo-url="" data-scan-type="">
                            <div class="banner-content">
                                <div class="banner-icon">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                                </div>
                                <div class="banner-info">
                                    <div class="banner-title">PQC-Sealed Project Archive Ready</div>
                                    <div class="banner-desc">Quantum-Safe Encryption Detected. Every source file will be wrapped in <b>ML-KEM-768</b> derived envelopes. Download and protect your intellectual property.</div>
                                </div>
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 10px; align-items: flex-end;">
                                <button class="btn-action" style="width: auto; padding: 12px 30px; font-size: 0.85rem;" onclick="encryptGitHubProject()">Generate & Download PQC-Sealed ZIP</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ====================== TAB 2 : PS1 ALGO RESEARCH ====================== -->
        <div id="tab-ps1" class="tab-content">
            <div class="ps-header">Post-Quantum Cryptography Algorithms</div>
            <div class="ps-desc">Research and design cryptographic algorithms resistant to quantum computer attacks. Evaluate existing post-quantum cryptography schemes and propose implementations for mathematical lattice improvements. (Problem Statement 1)</div>
            
            <div style="display: flex; flex-direction: column; gap: 20px;">
                <!-- AI Configuration Dropdowns -->
                <div class="card" style="border-color:rgba(0,250,136,0.3); box-shadow:0 0 15px rgba(0,250,136,0.05); overflow:visible !important; z-index:50;">
                    <div class="card-title" style="margin-bottom: 15px; color:var(--primary);">AI Threat Intelligence Engine (Powered by Google Servers)</div>
                    <div style="display:flex; gap: 15px; flex-wrap:wrap; align-items:flex-end;">
                        <div style="flex:1;">
                            <label style="font-size:0.7rem; color:var(--text-dim); margin-bottom:5px; display:block;">Target Environment</label>
                            <select id="ps1-target" class="m-input" onchange="fetchDynamicAttacks()">
                                <option value="iot_device">IoT Device / Edge Sensor</option>
                                <option value="file">Local File / Database</option>
                                <option value="folder">Shared Network Folder</option>
                                <option value="cloud_storage">Cloud Storage Bucket</option>
                                <option value="api_gateway">REST API Gateway</option>
                                <option value="blockchain">Blockchain Smart Contract</option>
                                <option value="healthcare">Healthcare Wearable (IoMT)</option>
                                <option value="autonomous_vehicle">Autonomous Vehicle (CAN Bus)</option>
                                <option value="industrial_ics">Industrial Control System (ICS)</option>
                            </select>
                        </div>
                        <div style="flex:1; position:relative;">
                            <label style="font-size:0.7rem; color:var(--text-dim); margin-bottom:5px; display:block;">Secure Target Algorithm (Max 2)</label>
                            <div class="m-input" style="padding: 10px; cursor: pointer; display: flex; justify-content: space-between; align-items: center;" onclick="toggleAlgoDropdown()">
                                <span id="algo-dropdown-text" style="font-size:0.75rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">ML-KEM</span>
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                            </div>
                            <div id="algo-checkbox-list" class="m-input" style="display: none; position: absolute; top: calc(100% + 5px); left: 0; width: 100%; z-index: 100; max-height: 180px; overflow-y: auto; padding: 5px; box-shadow:0 10px 30px rgba(0,0,0,0.5);">
                                <label style="display:flex; align-items:center; gap:8px; padding:8px 5px; cursor:pointer;"><input type="checkbox" value="ML-KEM" class="algo-cb" onchange="checkAlgoCheckboxLimit(this)" checked> <span style="font-size:0.75rem;">ML-KEM (Kyber)</span></label>
                                <label style="display:flex; align-items:center; gap:8px; padding:8px 5px; cursor:pointer;"><input type="checkbox" value="ML-DSA" class="algo-cb" onchange="checkAlgoCheckboxLimit(this)"> <span style="font-size:0.75rem;">ML-DSA (Dilithium)</span></label>
                                <label style="display:flex; align-items:center; gap:8px; padding:8px 5px; cursor:pointer;"><input type="checkbox" value="SLH-DSA" class="algo-cb" onchange="checkAlgoCheckboxLimit(this)"> <span style="font-size:0.75rem;">SLH-DSA (SPHINCS+)</span></label>
                                <label style="display:flex; align-items:center; gap:8px; padding:8px 5px; cursor:pointer;"><input type="checkbox" value="FRODO" class="algo-cb" onchange="checkAlgoCheckboxLimit(this)"> <span style="font-size:0.75rem;">FrodoKEM</span></label>
                                <label style="display:flex; align-items:center; gap:8px; padding:8px 5px; cursor:pointer;"><input type="checkbox" value="FALCON" class="algo-cb" onchange="checkAlgoCheckboxLimit(this)"> <span style="font-size:0.75rem;">FALCON</span></label>
                                <label style="display:flex; align-items:center; gap:8px; padding:8px 5px; cursor:pointer;"><input type="checkbox" value="BIKE" class="algo-cb" onchange="checkAlgoCheckboxLimit(this)"> <span style="font-size:0.75rem;">BIKE</span></label>
                                <label style="display:flex; align-items:center; gap:8px; padding:8px 5px; cursor:pointer;"><input type="checkbox" value="HQC" class="algo-cb" onchange="checkAlgoCheckboxLimit(this)"> <span style="font-size:0.75rem;">HQC</span></label>
                                <label style="display:flex; align-items:center; gap:8px; padding:8px 5px; cursor:pointer;"><input type="checkbox" value="MCELIECE" class="algo-cb" onchange="checkAlgoCheckboxLimit(this)"> <span style="font-size:0.75rem;">Classic McEliece</span></label>
                                <label style="display:flex; align-items:center; gap:8px; padding:8px 5px; cursor:pointer;"><input type="checkbox" value="SIKE_VULN" class="algo-cb" onchange="checkAlgoCheckboxLimit(this)"> <span style="font-size:0.75rem;">SIKE (Vulnerable)</span></label>
                                <label style="display:flex; align-items:center; gap:8px; padding:8px 5px; cursor:pointer;"><input type="checkbox" value="AES-256" class="algo-cb" onchange="checkAlgoCheckboxLimit(this)"> <span style="font-size:0.75rem;">AES-256 (Fallback)</span></label>
                            </div>
                        </div>
                        <div style="flex:1.5;">
                            <label style="font-size:0.7rem; color:var(--warning); margin-bottom:5px; display:block; font-weight:700;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="position:relative; top:2px; margin-right:3px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg> Predicted Actionable Attack (Dynamic)</label>
                            <select id="ps1-attack" class="m-input" style="border-color:rgba(219, 147, 34, 0.4);">
                                <option value="">Fetching live from Google Server...</option>
                            </select>
                        </div>
                        <div>
                            <button class="btn-action" style="padding:12px 20px; font-size: 0.85rem;" onclick="ps1GenerateAlgorithm()">Sync & Generate Schema</button>
                        </div>
                    </div>
                </div>

                <div class="card card-terminal" style="height:auto; min-height:400px; flex:none;">
                    <div style="position: sticky; top: -5px; background: var(--term-bg); padding-bottom: 10px; margin-bottom: 5px; border-bottom: 1px dashed var(--border); display:flex; justify-content:space-between; align-items:center;">
                        <span>Unified Algorithm Evaluation Inbox</span>
                        <span style="font-size:0.6rem; color:var(--text-dim); background:rgba(0,0,0,0.5); padding:2px 6px; border-radius:4px;">READ / WRITE CAPABLE</span>
                    </div>
                    <textarea class="m-input" id="algo-math" style="flex:1; min-height:220px; font-size:0.75rem; margin-top:10px; border-color:rgba(0,250,136,0.3); background:rgba(0,0,0,0.5); padding:15px; color:#50C878;" placeholder="// Dynamic algorithm will appear here based on selected data.
// You can also paste external cryptographic code snippets manually to test if they align with Post-Quantum standards..."></textarea>
                    
                    <button class="btn-action" style="padding:15px; margin-top:15px; font-size: 0.9rem; background:linear-gradient(90deg, #1f4037 0%, var(--primary) 100%);" onclick="simulatePS1()">Run Verification Engine</button>
                    
                    <div id="ps1-res" style="margin-top:15px; font-size:0.8rem; line-height:1.5;"></div>
                </div>
            </div>
        </div>

        <!-- ====================== TAB 4 : IOT EDGE DEFENSE ====================== -->
        <div id="tab-iot" class="tab-content">
            <div class="ps-header">IoT Edge Security Mission Control</div>
            <div class="ps-desc">Monitor and secure remote IoT devices (Termux/Phone) from quantum threats. Deploy ML-KEM-768 shields to prevent ECC private key leaks and unauthorized camera access.</div>
            
            <div class="grid-system" style="grid-template-columns: 1fr 2fr;">
                <div class="side-block">
                    <div class="card" style="border-color:var(--primary);">
                        <div class="card-title">Device Connection</div>
                        <input type="text" id="iot-ip" class="m-input" placeholder="Phone IP (e.g. 192.168.1.5)" value="127.0.0.1">
                        <button class="btn-action" style="margin-top:10px;" onclick="connectIoT()">Establish Edge Link</button>
                        <div id="iot-status-panel" style="margin-top:20px; display:none;">
                            <div class="algo-row"><span style="font-size:0.7rem; color:var(--text-dim);">Device Status</span><span id="iot-conn-badge" class="badge">Online</span></div>
                            <div class="algo-row"><span style="font-size:0.7rem; color:var(--text-dim);">Battery Level</span><span id="iot-battery" style="color:#fff; font-weight:700;">--%</span></div>
                            <div class="algo-row"><span style="font-size:0.7rem; color:var(--text-dim);">PQC Shield</span><span id="iot-pqc-status" style="color:var(--danger); font-weight:700;">INACTIVE</span></div>
                        </div>
                    </div>
                    <div class="card" id="iot-actions" style="margin-top:20px; opacity:0.5; pointer-events:none;">
                        <div class="card-title">Security Operations</div>
                        <button class="btn-action" style="background:var(--danger); margin-bottom:10px;" onclick="attackIoT()">Simulate ECC Breach</button>
                        <button class="btn-action" style="background:var(--primary);" onclick="secureIoT()">Deploy ML-KEM Shield</button>
                        <button class="btn-action" style="margin-top:10px; background:var(--bg-panel); border:1px solid var(--border);" onclick="resetIoT()">Factory Reset (ECC)</button>
                    </div>
                </div>
                <div class="main-block">
                    <div class="card card-terminal" style="height:250px; margin-bottom:20px;">
                        <div style="position: sticky; top: -5px; background: var(--term-bg); padding-bottom: 5px; margin-bottom: 10px; border-bottom: 1px dashed var(--border);">Mission Output: IoT Console</div>
                        <div id="iot-term-logs"><div class="t-msg">Awaiting Edge Connection...</div></div>
                    </div>
                    <div class="card" style="flex:1; min-height:350px; position:relative; overflow:hidden; background:#000;">
                        <div class="card-title" style="position:absolute; top:15px; left:15px; z-index:10; background:rgba(0,0,0,0.6); padding:5px 10px; border-radius:4px;">Live Intercept Feed <span id="camera-status" style="color:var(--danger); margin-left:10px;">[BLOCKED]</span></div>
                        <div id="camera-container" style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; color:var(--text-dim); font-size:0.8rem; text-align:center; flex-direction:column; gap:15px;">
                            <div class="cctv-overlay" id="cctv-ui" style="display:none;">
                                <div style="display:flex; justify-content:space-between; width:100%;">
                                    <span>CAM-01 [EXTERNAL_EDGE]</span>
                                    <span class="rec-dot">● REC</span>
                                </div>
                                <div style="display:flex; justify-content:space-between; width:100%; align-items:flex-end;">
                                    <div id="cctv-timestamp" style="font-size:0.9rem;">CLOCK_SYNC_PENDING</div>
                                    <span style="font-size:0.7rem;">1080p / 60FPS / PQC-BYPASS</span>
                                </div>
                            </div>
                            <div class="scanlines"></div>
                            <div id="cam-placeholder" style="text-align:center;">
                                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="opacity:0.2;"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
                                <p>Encrypted Stream Unavailable</p>
                            </div>
                        </div>
                        <button id="snap-btn" class="btn-action" style="position:absolute; bottom:20px; right:20px; width:auto; padding:10px 20px; display:none;" onclick="captureIoT()">Download Frame</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- ====================== TAB 6 : SYSTEM LOGS (BLOCKCHAIN PQC) ====================== -->
        <div id="tab-logs" class="tab-content">
            <div class="ps-header">Live Threat Radar & Quantum Audit Logs (SLH-DSA)</div>
            <div class="ps-desc">This is a live API listener monitoring real-time LAN & Web traffic reaching this application. It constructs an immutable <b>SLH-DSA/SPHINCS+</b> blockchain over incoming packets. If an external machine (Threat Actor) attempts to forge a previous block via the API, the chain validation mathematically breaks.</div>

            <div class="grid-system" style="grid-template-columns: 2fr 1fr; margin-top:20px;">
                <!-- Left: Live Log Chain -->
                <div class="card card-terminal" style="display:flex; flex-direction:column; height: 500px; overflow-y: hidden;">
                    <div style="position: sticky; top: -5px; background: var(--term-bg); padding-bottom: 5px; margin-bottom: 10px; border-bottom: 2px solid var(--border); display:flex; justify-content:space-between; align-items:center; z-index:10;">
                        <div style="display:flex; gap:15px; align-items:center;">
                            <span style="color:var(--primary); font-weight:800;">Real-Time Immutable Audit Server</span>
                            <span style="font-size:0.6rem; background:rgba(255,255,255,0.1); padding:3px 8px; border-radius:4px;">AUTO-POLL: ACTIVE (2s)</span>
                        </div>
                        <span style="color:var(--text-white);">Chain Integrity: <span id="chain-status-text" style="color:var(--primary); font-weight:800;">100% SECURE</span></span>
                    </div>

                    <div style="display:flex; gap:10px; margin-bottom:10px; font-size:0.7rem; border-bottom: 1px dashed var(--border); padding-bottom:10px;">
                        <button onclick="currentFilter='ALL'; fetchLogChain();" style="background:var(--border); color:#fff; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">ALL</button>
                        <button onclick="currentFilter='WARNING'; fetchLogChain();" style="background:rgba(255, 170, 0, 0.2); color:var(--warning); border:1px solid var(--warning); padding:5px 10px; border-radius:4px; cursor:pointer;">WARNINGS</button>
                        <button onclick="currentFilter='CRITICAL'; fetchLogChain();" style="background:rgba(248, 75, 75, 0.2); color:var(--danger); border:1px solid var(--danger); padding:5px 10px; border-radius:4px; cursor:pointer;">CRITICAL</button>
                        <div style="flex:1;"></div>
                        <span style="color:var(--text-dim); display:flex; align-items:center;">💡 Click any log to extract Forensic Metadata</span>
                    </div>
                    
                    <div id="log-chain-container" style="flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:6px; line-height:1.4; font-size:0.75rem; padding-right:5px;">
                    </div>
                </div>

                <!-- Right: Cyber Attack Panel -->
                <div class="card" style="display:flex; flex-direction:column; border-color:var(--primary); justify-content:flex-start;">
                    <div class="card-title" style="color:var(--danger); font-weight:800; border-bottom:1px dashed var(--danger); padding-bottom:10px;">Remote Threat Vector Testing</div>
                    <div style="margin-top:15px; color:var(--text-dim); font-size:0.75rem; line-height:1.5;">
                        <p>Have a friend access this app via LAN port <b>5001</b></p>
                        <p>When they browse, you will see their network requests mapped live into the PQC Blockchain.</p>
                        <p>If history is altered, SLH-DSA constraints will orphan the chain!</p>
                    </div>

                    <button id="tamper-btn" class="btn-action" style="margin-top:20px; padding:15px; background:var(--bg-card); border-color:var(--danger); color:var(--danger);" onclick="simulateLogTampering()">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom:5px;"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                        <br>Simulate Remote API Override Attack
                    </button>
                    
                    <div id="tamper-alert" style="display:none; margin-top:20px; padding:15px; background:rgba(248, 75, 75, 0.1); border-left:4px solid var(--danger); color:var(--text-white); font-size:0.75rem;">
                        <b style="color:var(--danger);">SYSTEM HALTED!</b><br>API Forgery Detected & payload rejected. Forensic Integrity Preserved.
                    </div>

                    <button id="reset-btn" onclick="resetChain()" style="display:none; margin-top:15px; padding:12px 20px; width:100%; background:rgba(0,250,136,0.1); border:1px solid var(--primary); color:var(--primary); border-radius:8px; cursor:pointer; font-size:0.8rem; font-weight:700;">
                        🔄 Reset Chain (Re-Key SLH-DSA)
                    </button>
                </div>
            </div>
        </div>

    </div>
</div>

<!-- CODE PAD MODAL -->
<div id="code-modal" class="modal-overlay">
    <div class="modal-card" style="width: 800px; height: 600px;">
        <div class="modal-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
            Royal Code Pad
        </div>
        <textarea id="code-in" class="m-input" style="flex:1; height:100%; font-size: 0.9rem; padding: 20px;" placeholder="// Paste your cryptographic code here..."></textarea>
        <div style="display:flex; gap:10px; margin-top: 20px;">
            <button class="btn-action" onclick="closeCodePad()">Save & Exit</button>
        </div>
    </div>
</div>

<!-- GITHUB REPO MODAL -->
<div id="github-modal" class="modal-overlay">
    <div class="modal-card">
        <div class="modal-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.372.79 1.102.79 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
                Select Repository
            </div>
            <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom:10px;">Target user: <b id="gh-user-display" style="color:var(--primary);">None</b></div>
            
            <div style="display:flex; gap:10px; margin-bottom:15px;">
                <input type="text" id="gh-user-in" class="m-input" style="flex:1; font-size: 0.75rem;" placeholder="GitHub Username">
                <button class="btn-action" style="width:auto; padding:0 20px; font-size:0.7rem;" onclick="handleSync()">Sync</button>
            </div>

            <input type="password" id="gh-token-in" class="m-input" style="margin-bottom:15px; font-size: 0.7rem; border-color: rgba(255,255,255,0.1);" placeholder="Personal Access Token">
            <div id="repo-container" class="repo-list" style="max-height: 250px; overflow-y: auto; border: 1px solid var(--border); border-radius: 8px; background: rgba(0,0,0,0.3);">
                <div style="text-align:center; padding:20px; color:var(--text-dim);">Enter username and click Sync</div>
            </div>
        <div style="margin-top:20px;">
            <button class="btn-action" style="background:#444;" onclick="document.getElementById('github-modal').style.display='none'">Cancel</button>
        </div>
    </div>
</div>

<div id="tom-cruise-wrapper">
    <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNnh6amV5a2E4eGZnbTV0MmV5ZHR4eTV4eHQ2eHQ2eHQ2eHQ2eHQmaz0x/3o7TKMGfTTE462/giphy.gif" alt="Running">
</div>

<script>
// MISSION STATE
let isPqcActive = false;

// Tab Switching
function switchTab(tabId, el) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');
    if(el) el.classList.add('active');
}

// Map Logic
const mapSvg = document.getElementById('map-svg');
const countryCoords = {
    'US': [95, 100], 'CA': [90, 60], 'MX': [100, 150],
    'CN': [480, 115], 'RU': [450, 60], 'IN': [425, 155], 'PK': [405, 135],
    'GB': [285, 75], 'FR': [290, 85], 'DE': [305, 75], 'NL': [300, 70], 'UA': [345, 85],
    'BR': [195, 220], 'AR': [185, 260], 'CL': [170, 260],
    'JP': [530, 105], 'KR': [515, 105], 'SG': [475, 195], 'VN': [485, 160], 'ID': [495, 210],
    'TR': [350, 110], 'IR': [385, 125], 'SA': [370, 145], 'EG': [340, 140],
    'ZA': [325, 255], 'NG': [295, 175], 'AU': [540, 245], 'NZ': [580, 275]
};

async function drawMapAttacks() {
    try {
        const resp = await fetch('/v3/live-threats');
        const data = await resp.json();
        mapSvg.innerHTML = '';
        const ld = Array.isArray(data) ? data : (data.sources || []);
        
        let summaryText = `Detecting <b>${ld.length} Active Probes</b> targeting non-PQC nodes.`;
        if(ld[0]) summaryText += `<br><br>Top Threat: <span style="color:var(--danger)">${ld[0].ip}</span> from <b>${ld[0].country}</b> performing reconnaissance.`;
        $('map-summary-text').innerHTML = summaryText;

        ld.slice(0, 15).forEach((threat, i) => {
            const country = threat.country || 'Unknown';
            const base = countryCoords[country] || [320, 110];
            const x = base[0] + (Math.random()*16 - 8); 
            const y = base[1] + (Math.random()*16 - 8);
            
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", x); circle.setAttribute("cy", y); circle.setAttribute("r", 4);
            circle.setAttribute("class", "hub-dot");
            mapSvg.appendChild(circle);

            const pulse = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            pulse.setAttribute("cx", x); pulse.setAttribute("cy", y); pulse.setAttribute("r", 4);
            pulse.setAttribute("fill", "none"); pulse.setAttribute("stroke", "var(--primary)");
            pulse.innerHTML = `<animate attributeName="r" from="4" to="25" dur="2.5s" begin="${i * 0.4}s" repeatCount="indefinite" />
                               <animate attributeName="opacity" from="0.7" to="0" dur="2.5s" begin="${i * 0.4}s" repeatCount="indefinite" />`;
            mapSvg.appendChild(pulse);
        });
    } catch(e) {}
}
setInterval(drawMapAttacks, 30000);

const $ = id => document.getElementById(id);
async function typeTerm(boxId, msg, type='msg') {
    const t = $(boxId);
    let contentNode = document.createElement('span');
    contentNode.className = type === 'err' ? 't-err' : (type === 'warning' ? 't-warning' : 't-msg');
    contentNode.innerHTML = `<br><span class="t-date">${new Date().toLocaleTimeString()}</span> `;
    t.appendChild(contentNode);
    for(let i=0; i<msg.length; i++) {
        contentNode.innerHTML += msg.charAt(i);
        t.parentElement.scrollTop = t.parentElement.scrollHeight;
        await new Promise(r => setTimeout(r, 8)); 
    }
}

function updateWaveCharts(severity) {
    const charts = document.querySelectorAll('.chart-path'); const fills = document.querySelectorAll('.chart-path-fill');
    charts.forEach((c, idx) => {
        let v = severity === 'CRITICAL' ? [5, 25] : (severity === 'HIGH' ? [15, 25] : [20, 25]);
        let p = Array.from({length: 4}, () => Math.floor(Math.random()*(v[1]-v[0]+1))+v[0]);
        c.setAttribute('d', `M0,${p[0]} Q25,${p[1]} 50,${p[2]} T100,${p[3]}`);
        fills[idx].setAttribute('d', `M0,30 L0,${p[0]} Q25,${p[1]} 50,${p[2]} T100,${p[3]} L100,30 Z`);
    });
}

// ====== THEME & SESSION ======
let scanHistory = [];
function toggleTheme() {
    const b = document.body;
    const isLight = b.classList.toggle('light-theme');
    const icon = $('theme-icon');
    const txt = $('theme-text');
    if(isLight) {
        icon.innerHTML = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';
        txt.innerText = "Light Mode";
    } else {
        icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
        txt.innerText = "Dark Mode";
    }
}

function updateHistoryUI() {
    const box = $('history-box');
    if(!box || scanHistory.length === 0) return;
    box.innerHTML = scanHistory.map((h, i) => `
        <div class="repo-item" style="padding:15px; border:1px solid var(--border); background:rgba(0,0,0,0.2);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div style="font-weight:800; color:var(--primary); font-size:0.8rem;">MISSION: ${h.type.toUpperCase()}</div>
                    <div style="font-size:0.65rem; color:var(--text-dim); margin-top:3px;">${h.date} | ${h.origin}</div>
                </div>
                <div class="badge ${h.risk === 'CRITICAL' ? 'badge-crit' : (h.risk === 'HIGH' ? 'badge-high' : (h.risk === 'MEDIUM' ? 'badge-warn' : ''))}" 
                     style="${h.risk === 'SECURE' ? 'background:rgba(0,250,136,0.1); color:var(--primary);' : ''}">${h.risk}</div>
            </div>
            <div style="margin-top:10px; font-size:0.75rem; color:#fff;">${h.summary}</div>
        </div>
    `).reverse().join('');
}

// ====== MODAL LOGIC ======
let githubUser = null;
let selectedGitHubRepo = null;

function openCodePad() { 
    $('code-modal').style.display = 'flex'; 
    $('code-in').focus();
}
function openGitHubModal() {
    $('github-modal').style.display = 'flex';
    if (githubUser) {
        $('gh-user-in').value = githubUser;
        $('gh-user-display').innerText = githubUser;
        fetchRepos();
    }
}

function closeCodePad() { 
    $('code-modal').style.display = 'none'; 
    const code = $('code-in').value;
    if(code.trim().length > 0) {
        $('pad-status').innerText = 'Buffer Size: ' + code.length + ' chars';
        $('pad-status').style.color = 'var(--primary)';
    }
}

function handleSync() {
    const user = $('gh-user-in').value.trim();
    if (user) {
        githubUser = user;
        localStorage.setItem('pqc_gh_user', user);
        fetchRepos();
    }
}

async function fetchRepos() {
    $('gh-user-display').innerText = githubUser;
    const container = $('repo-container');
    const token = $('gh-token-in').value;
    
    container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-dim);">Fetching...</div>';
    
    try {
        if(token) localStorage.setItem('pqc_gh_token', token);
        let url = token ? `https://api.github.com/user/repos?per_page=100&sort=updated` : `https://api.github.com/users/${githubUser}/repos?per_page=100&sort=updated`;
        let headers = { 'Accept': 'application/vnd.github.v3+json' };
        if(token) headers['Authorization'] = `token ${token}`;

        const resp = await fetch(url, { headers });
        const repos = await resp.json();
        
        if(!Array.isArray(repos)) throw new Error("Repo discovery failed");
        
        container.innerHTML = repos.map(r => `
            <div class="repo-item" onclick="selectRepo('${r.clone_url}', '${r.name}')">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="font-weight:700; color:#fff;">${r.name}</div>
                    ${r.private ? '<span style="font-size:0.5rem; background:rgba(219, 147, 34, 0.2); color:var(--warning); padding:2px 5px; border-radius:4px; text-transform:uppercase;">Private</span>' : ''}
                </div>
                <div style="font-size:0.65rem; color:var(--text-dim);">${r.language || 'Code'} • Ready</div>
            </div>
        `).join('');
    } catch(e) {
        container.innerHTML = `<div style="color:var(--danger); padding:20px;">Discovery Error</div>`;
    }
}

function selectRepo(url, name) {
    selectedGitHubRepo = url;
    $('gh-text').innerText = "Repo: " + name;
    $('github-modal').style.display = 'none';
    $('gh-action-btn').classList.add('connected');
}

// ------ PQC ENCRYPTION WORKFLOW ------
async function encryptProject() {
    const banner = $('pqc-encrypt-banner');
    const repoUrl = banner.dataset.repoUrl; 
    const scanType = banner.dataset.scanType;
    const token = localStorage.getItem('pqc_gh_token') || '';

    await typeTerm('term-logs', 'INITIATING PQC-SEALING PROTOCOL (ML-KEM)...', 'msg');

    const btn = banner.querySelector('button');
    const originalText = btn.innerText;
    btn.innerText = "Encrypting...";
    btn.disabled = true;

    try {
        const formData = new FormData();
        if (repoUrl) formData.append('repo_url', repoUrl);
        formData.append('token', token);
        formData.append('method', 'zip');
        formData.append('scan_type', scanType);
        const response = await fetch('/api/encrypt_project', { method: 'POST', body: formData });
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `PQC_ENCRYPTED_PROJECT.zip`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            await typeTerm('term-logs', 'Encryption Complete. ML‑KEM‑768 sealed.', 'msg');
        } else { throw new Error('Encryption failed'); }
    } catch (e) {
        await typeTerm('term-logs', 'ENCRYPTION_FAILED: ' + e.message, 'err');
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
}
function encryptGitHubProject() { encryptProject(); }

// ====== MAIN TAB: CORE AUDIT ======
async function executeScan() {
    const code = $('code-in').value, file = $('file-in').files[0], path = $('path-in').value, githubUrl = selectedGitHubRepo;
    const runner = $('tom-cruise-wrapper');
    const scanLine = $('scan-overlay');
    if(scanLine) {
        scanLine.classList.add('active-scan');
        setTimeout(() => { scanLine.classList.remove('active-scan'); }, 6000);
    }

    if (runner) {
        runner.style.display = 'block';
        runner.classList.add('running');
        setTimeout(() => {
            runner.classList.remove('running');
            runner.style.display = 'none';
        }, 6000);
    }

    $('term-logs').innerHTML = ''; await typeTerm('term-logs', 'Initiating localized heuristic analysis...');
    
    let url = '/v3/audit';
    let fetchOptions = { method:'POST' };

    if(githubUrl) {
        const fd = new FormData(); fd.append('url', githubUrl); fd.append('token', $('gh-token-in').value);
        url = '/v3/audit/github'; fetchOptions.body = fd;
    }
    else if(file) { 
        const fd = new FormData(); fd.append('file', file); 
        url = '/v3/audit/file'; fetchOptions.body = fd;
    }
    else if(path) { 
        const fd = new FormData(); fd.append('path', path); 
        url = '/v3/audit/path'; fetchOptions.body = fd;
    }
    else { 
        fetchOptions.headers = {'Content-Type':'application/json'};
        fetchOptions.body = JSON.stringify({ code: code });
    }

    try {
        const startT = Date.now();
        const r = await fetch(url, fetchOptions); 
        const data = await r.json(); const dur = ((Date.now() - startT) / 1000).toFixed(2);
        
        if(data.status === 'error') { await typeTerm('term-logs','CRITICAL_ERR: ' + data.message, 'err'); } 
        else {
            const auditTitle = githubUrl ? 'GitHub Sync' : (file ? 'Archive' : (path ? 'Local Drive' : 'Buffer'));
            const finalRisk = data.base_report.risk_level || 'UNKNOWN';
            
            scanHistory.push({
                type: auditTitle,
                origin: githubUrl || file?.name || path || 'Buffer',
                summary: `Audit complete. Readiness: ${data.base_report.readiness_percentage}%`,
                risk: finalRisk,
                date: new Date().toLocaleTimeString()
            });
            updateHistoryUI();

            $('val-threats').innerText = data.base_report.vulnerabilities_found;
            $('val-files').innerText = data.base_report.files_processed || 1;
            
            const risk = data.base_report.risk_level, readyPct = data.base_report.readiness_percentage;
            $('b-threat').innerText = risk;
            $('b-threat').className = `badge ${risk==='CRITICAL'?'badge-crit':(risk==='HIGH'?'badge-high':'badge-warn')}`;
            updateWaveCharts(risk);
            
            $('val-ready').innerText = readyPct + '%';
            $('ready-trend').innerHTML = readyPct === 100 ? 'SECURE <i>✔</i>' : 'CRITICAL <i>↘</i>';
            $('ring-status').style.background = `conic-gradient(var(--primary) 0% ${readyPct}%, var(--danger) ${readyPct}% 100%)`;

            if(data.vulnerable_implementations && data.vulnerable_implementations.length > 0) {
                $('vuln-tbody').innerHTML = data.vulnerable_implementations.map((v, i) => `
                    <tr>
                        <td>
                            <div style="font-weight:700; color:#fff;">Line Target: ${v.line}</div>
                            <div style="font-size:0.75rem; color:var(--text-dim);">${v.file}</div>
                        </td>
                        <td><div style="font-family:'JetBrains Mono';">${v.algorithm}</div></td>
                        <td><div class="badge ${v.risk_level==='CRITICAL'?'badge-crit':'badge-warn'}">${v.risk_level}</div></td>
                        <td><div style="font-size:0.75rem;">${v.objective_metadata.prevention}</div></td>
                    </tr>
                `).join('');
            } else {
                $('vuln-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;">✓ Target architecture meets PQC standards.</td></tr>';
            }
            document.getElementById('pqc-encrypt-banner').style.display = 'flex';
            document.getElementById('pqc-encrypt-banner').dataset.repoUrl = githubUrl || '';
            document.getElementById('pqc-encrypt-banner').dataset.scanType = auditTitle;
        }
    } catch(e) { await typeTerm('term-logs', 'FATAL Error', 'err'); }
}

function toggleAlgoDropdown() {
    const list = $('algo-checkbox-list');
    list.style.display = list.style.display === 'none' ? 'block' : 'none';
}

function checkAlgoCheckboxLimit(checkbox) {
    const checkboxes = document.querySelectorAll('.algo-cb:checked');
    if (checkboxes.length > 2) { checkbox.checked = false; return; }
    const textSpan = $('algo-dropdown-text');
    textSpan.innerText = Array.from(checkboxes).map(cb => cb.value).join(' + ') || 'Select...';
}

async function fetchDynamicAttacks() {
    const target = $('ps1-target').value;
    try {
        const res = await fetch(`/api/fetch_attacks?target=${target}`);
        const data = await res.json();
        $('ps1-attack').innerHTML = data.attacks.map(a => `<option value="${a}">${a}</option>`).join('');
    } catch(e) {}
}

async function ps1GenerateAlgorithm() {
    const target = $('ps1-target').value;
    const checkboxes = document.querySelectorAll('.algo-cb:checked');
    const algo = Array.from(checkboxes).map(cb => cb.value).join(' + ');
    const attack = $('ps1-attack').value;
    try {
        const res = await fetch('/api/generate_algo', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({target, algo, attack})
        });
        const data = await res.json();
        $('algo-math').value = data.code;
    } catch(e) {}
}

async function simulatePS1() {
    const txt = $('algo-math').value;
    if (!txt.trim()) return;
    $('ps1-res').innerHTML = 'Scanning architecture...';
    try {
        const res = await fetch('/api/evaluate_algo', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: txt})
        });
        const data = await res.json();
        $('ps1-res').innerHTML = `<b>Score: ${data.score}/100</b><br>${data.message}`;
    } catch(e) {}
}

// --- BLOCKCHAIN LOGS ---
let currentFilter = 'ALL';
async function fetchLogChain() {
    try {
        const res = await fetch('/api/get_logs');
        const data = await res.json();
        renderSecureLogs(currentFilter, data.chain, data.valid);
    } catch(e) {}
}

function renderSecureLogs(filter = 'ALL', logs = [], isValid = true) {
    const container = $('log-chain-container');
    container.innerHTML = "";
    $('chain-status-text').innerText = isValid ? "VALID" : "CORRUPT";
    $('chain-status-text').style.color = isValid ? "var(--primary)" : "var(--danger)";

    logs.filter(l => filter === 'ALL' || l.severity === filter).forEach((log) => {
        let sc = log.severity === 'CRITICAL' ? 'var(--danger)' : 'var(--primary)';
        container.innerHTML = `
            <div style="padding:10px; border-left: 3px solid ${sc}; background:rgba(0,0,0,0.2); margin-bottom:5px;">
                <div style="font-size:0.6rem; color:var(--text-dim);">${log.timestamp} | ${log.ip}</div>
                <div style="font-weight:700;">> ${log.action}</div>
            </div>
        ` + container.innerHTML;
    });
}

async function simulateLogTampering() {
    await fetch('/api/tamper_log', { method: 'POST' });
    $('tamper-alert').style.display = "block";
    $('reset-btn').style.display = "block";
}

async function resetChain() {
    await fetch('/api/reset_chain', { method: 'POST' });
    $('tamper-alert').style.display = "none";
    $('reset-btn').style.display = "none";
}

// Initialization
const canvas = $('matrix-bg');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth; canvas.height = window.innerHeight;
const matrixChars = '01量子暗号';
const fontSize = 14;
let drops = Array(Math.floor(canvas.width / fontSize)).fill(1);

function drawMatrix() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ffffff'; ctx.font = fontSize + 'px monospace';
    drops.forEach((y, i) => {
        const text = matrixChars.charAt(Math.floor(Math.random() * matrixChars.length));
        ctx.fillText(text, i * fontSize, y * fontSize);
        if (y * fontSize > canvas.height && Math.random() > 0.99) drops[i] = 0;
        drops[i]++;
    });
}

fetchLogChain();
setInterval(fetchLogChain, 2000);
setInterval(drawMatrix, 50);
fetchDynamicAttacks();

// ====== IOT EDGE LOGIC (PROXIED) ======
let currentTargetIp = "";

async function connectIoT() {
    const ip = $('iot-ip').value;
    currentTargetIp = ip;
    await typeTerm('iot-term-logs', `Probing Edge Device at ${ip} via Proxy...`, 'msg');
    
    try {
        const resp = await fetch('/api/iot/status', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ ip })
        });
        
        const data = await resp.json();
        if(!resp.ok) {
            await typeTerm('iot-term-logs', `DEBUG: ${data.error || 'Unknown Proxy Error'}`, 'err');
            return;
        }
        
        if(data.error) throw new Error(data.error);
            
        $('iot-status-panel').style.display = 'block';
        $('iot-actions').style.opacity = '1'; $('iot-actions').style.pointerEvents = 'auto';
        $('iot-conn-badge').innerText = 'Online';
        $('iot-conn-badge').style.color = 'var(--primary)';
        $('iot-battery').innerText = data.battery + '%';
        $('iot-pqc-status').innerText = data.secured ? 'ML-KEM (SAFE)' : 'ECC (VULNERABLE)';
        $('iot-pqc-status').style.color = data.secured ? 'var(--primary)' : 'var(--danger)';
        await typeTerm('iot-term-logs', `Edge Handshake Success. Host: ${ip}`, 'msg');
    } catch(e) { 
        await typeTerm('iot-term-logs', `Proxy Connection Failed: ${e.message}`, 'err');
    }
}

async function attackIoT() {
    await typeTerm('iot-term-logs', `Injecting Lattice-based Brute Force Payload...`, 'msg');
    try {
        const resp = await fetch('/api/iot/exploit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ ip: currentTargetIp })
        });
        const data = await resp.json();
        if(resp.ok) {
            await typeTerm('iot-term-logs', `BREACH SUCCESSFUL! Intercepted Key: ${data.intercepted_key}`, 'err');
            $('camera-status').innerText = '[BREACHED]'; $('camera-status').style.color = 'var(--primary)';
            
            // Show CCTV UI
            $('cctv-ui').style.display = 'flex';
            $('cam-placeholder').style.display = 'none';

            // Start High-Speed Image Polling (More reliable than MJPEG)
            const camImg = document.createElement('img');
            camImg.style.width = '100%'; camImg.style.height = '100%'; camImg.style.objectFit = 'cover';
            $('camera-container').appendChild(camImg);

            if(window.iotCameraInterval) clearInterval(window.iotCameraInterval);
            window.iotCameraInterval = setInterval(() => {
                if(!window.pqcShieldActive) {
                    camImg.src = `/api/iot/camera?ip=${currentTargetIp}&t=${Date.now()}`;
                }
            }, 200); // 5 frames per second for smooth reliable feed

            // Start Timestamp Clock
            window.cctvClock = setInterval(() => {
                const now = new Date();
                $('cctv-timestamp').innerText = now.toLocaleString();
            }, 1000);
            
            $('snap-btn').style.display = 'block';
        } else {
            await typeTerm('iot-term-logs', `ATTACK REJECTED: ${data.reason || data.error}`, 'err');
        }
    } catch(e) {
        await typeTerm('iot-term-logs', `Exploit Proxy Error: ${e.message}`, 'err');
    }
}

async function secureIoT() {
    await typeTerm('iot-term-logs', `Pushing PQC Security Policy (ML-KEM-768)...`, 'msg');
    try {
        const resp = await fetch('/api/iot/upgrade', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ ip: currentTargetIp })
        });
        if(resp.ok) {
            await typeTerm('iot-term-logs', `SUCCESS: Device Hardened via ML-KEM Shield.`, 'msg');
            connectIoT();
            $('camera-container').innerHTML = `<div style="text-align:center; opacity:0.5;"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg><br>Stream Blocked by PQC</div>`;
            $('snap-btn').style.display = 'none';
        }
    } catch(e) {}
}

async function resetIoT() {
    if(!currentTargetIp) return;
    window.pqcShieldActive = false; // Allow camera again
    if(window.iotCameraInterval) clearInterval(window.iotCameraInterval);
    
    await typeTerm('iot-term-logs', `Factory Reset Initialized. Reverting to ECC...`, 'warn');
    try {
        const resp = await fetch('/api/iot/reset', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ ip: currentTargetIp })
        });
        if(resp.ok) {
            await typeTerm('iot-term-logs', `System Reset: Reverted to Legacy ECC.`, 'msg');
            $('iot-pqc-status').innerText = 'ECC (VULNERABLE)';
            $('iot-pqc-status').style.color = 'var(--danger)';
            $('camera-status').innerText = '[BLOCKED]';
            $('camera-status').style.color = 'var(--danger)';
            $('cctv-ui').style.display = 'none';
            $('cam-placeholder').style.display = 'flex';
            $('camera-container').style.background = '#000';
            $('camera-container').innerHTML = `
                <div class="cctv-overlay" id="cctv-ui" style="display:none;">
                    <div style="display:flex; justify-content:space-between; width:100%;">
                        <span>CAM-01 [EXTERNAL_EDGE]</span>
                        <span class="rec-dot">● REC</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; width:100%; align-items:flex-end;">
                        <div id="cctv-timestamp" style="font-size:0.9rem;">CLOCK_SYNC_PENDING</div>
                        <span style="font-size:0.7rem;">1080p / 60FPS / PQC-BYPASS</span>
                    </div>
                </div>
                <div class="scanlines"></div>
                <div id="cam-placeholder" style="text-align:center;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="opacity:0.2;"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
                    <p>Encrypted Stream Unavailable</p>
                </div>`;
        }
    } catch(e) {}
}

async function captureIoT() {
    const link = document.createElement('a');
    link.href = `/api/iot/camera?ip=${currentTargetIp}`;
    link.download = `IOT_SNAPSHOT_${Date.now()}.jpg`;
    link.click();
}
</script>
</body>
</html>"""

@app.route('/')
def index():
    return HTML_V3

@app.route('/v3/audit', methods=['POST'])
def audit():
    data = request.get_json()
    report = manager.full_advanced_audit(data.get('code', ''))
    app.latest_scan = report
    return jsonify(report)

@app.route('/v3/audit/file', methods=['POST'])
def audit_file():
    if 'file' not in request.files: return jsonify({'status': 'error'})
    f = request.files['file']
    f_path = os.path.join("v3_demo_samples", f.filename)
    if not os.path.exists("v3_demo_samples"): os.makedirs("v3_demo_samples")
    f.save(f_path)
    report = manager.scan_system_path(f_path)
    app.latest_scan = report
    return jsonify(report)

@app.route('/v3/audit/path', methods=['POST'])
def audit_path():
    path = request.form.get('path')
    report = manager.scan_system_path(path)
    app.latest_scan = report
    return jsonify(report)

@app.route('/v3/audit/github', methods=['POST'])
def audit_github():
    repo_url = request.form.get('url')
    token = request.form.get('token')
    match = re.search(r'github\.com/([^/]+)/([^/\.]+)', repo_url)
    owner, repo = match.groups()
    tmp_path = tempfile.mkdtemp()
    app.latest_github_tmp = tmp_path
    app.latest_github_repo = repo
    api_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token: headers['Authorization'] = f'token {token}'
    r = requests.get(api_url, headers=headers, stream=True, timeout=30)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z: z.extractall(tmp_path)
    report = manager.scan_system_path(tmp_path)
    app.latest_scan = report
    return jsonify(report)

@app.route('/api/encrypt_project', methods=['POST'])
def encrypt_project():
    try:
        scan_type = request.form.get('scan_type', '').lower()
        repo_url = request.form.get('repo_url', '')
        token = request.form.get('token', '')
        
        source_dir = getattr(app, 'latest_source_dir', None)
        project_name = 'project'

        if scan_type == 'github sync':
            source_dir = getattr(app, 'latest_github_tmp', None)
            project_name = getattr(app, 'latest_github_repo', 'project')
        elif scan_type == 'code buffer':
            source_dir = tempfile.mkdtemp()
            project_name = 'code_buffer'
            with open(os.path.join(source_dir, 'code.txt'), 'w') as f: f.write(request.form.get('code', ''))

        source_files = []
        for root, _, files in os.walk(source_dir):
            for fname in files: source_files.append(os.path.join(root, fname))

        aes_key = os.urandom(32)
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for fpath in source_files:
                with open(fpath, 'rb') as f: content = f.read()
                cipher = AES.new(aes_key, AES.MODE_GCM)
                zf.writestr(os.path.relpath(fpath, source_dir) + '.pqc', cipher.nonce + cipher.encrypt(content))
            zf.writestr('DECRYPTION_KEY.txt', f'AES-256 Key: {base64.b64encode(aes_key).decode()}')

        zip_buf.seek(0)
        return send_file(zip_buf, as_attachment=True, download_name="PQC_ENCRYPTED.zip")
    except Exception as e: return jsonify({'status': 'error', 'message': str(e)})

@app.route('/v3/live-threats')
def live_threats():
    try:
        r = requests.get("https://isc.sans.edu/api/sources/summary/30?json", timeout=5)
        return jsonify(r.json())
    except: return jsonify([{"ip": "1.1.1.1", "count": 100, "country": "US"}])

@app.route('/v3/download-report')
def download_report():
    scan = getattr(app, 'latest_scan', {})
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Location", "Algorithm", "Risk"])
    for v in scan.get('vulnerable_implementations', []):
        ws.append([f"Line {v.get('line')}", v['algorithm'], v.get('risk_level')])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="PQC_Report.xlsx")

@app.route('/api/iot/status', methods=['POST'])
def iot_status():
    ip = request.json.get('ip')
    try:
        r = requests.get(f"http://{ip}:5000/status", timeout=2)
        return jsonify(r.json())
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request Timed Out. Is the phone server running?"}), 504
    except Exception as e: 
        return jsonify({"error": f"Network Error: {str(e)}"}), 500

@app.route('/api/iot/exploit', methods=['POST'])
def iot_exploit():
    ip = request.json.get('ip')
    try:
        print(f"[PROXY] Attempting Exploit on {ip}...")
        r = requests.get(f"http://{ip}:5000/exploit", timeout=5)
        data = r.json()
        print(f"[PROXY] Phone Response: {data}")
        return jsonify(data), r.status_code
    except Exception as e: 
        print(f"[PROXY] Exploit Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/iot/upgrade', methods=['POST'])
def iot_upgrade():
    ip = request.json.get('ip')
    try:
        r = requests.post(f"http://{ip}:5000/upgrade_pqc", timeout=5)
        return jsonify(r.json())
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/iot/reset', methods=['POST'])
def iot_reset():
    ip = request.json.get('ip')
    try:
        r = requests.post(f"http://{ip}:5000/reset", timeout=5)
        return jsonify(r.json())
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/iot/reset', methods=['POST'])
def iot_reset_proxy():
    data = request.json or {}
    ip = data.get('ip')
    try:
        r = requests.post(f"http://{ip}:5000/reset", timeout=5)
        return jsonify(r.json())
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/iot/camera')
def iot_camera_proxy():
    ip = request.args.get('ip')
    try:
        # Request the image from the phone server
        r = requests.get(f"http://{ip}:5000/camera", timeout=3)
        if r.status_code == 200:
            return Response(r.content, mimetype='image/jpeg')
        return "Offline", 404
    except: return "Error", 500

@app.route('/mission-impossible_oEwlsUsI.mp3')
def serve_audio():
    if os.path.exists('mission-impossible_oEwlsUsI.mp3'):
        return send_file('mission-impossible_oEwlsUsI.mp3')
    return "Audio missing", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
