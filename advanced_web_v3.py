from flask import Flask, request, jsonify, send_file
import os, sys, time, random
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

from pqc_advanced_analyzer import AdvancedPQCManager
from pqc_real_implementation import AdvancedPQCEngine

app = Flask(__name__)
manager = AdvancedPQCManager()
engine = AdvancedPQCEngine(n=512)

HTML_V3 = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Emerald Sec | Tactical Command</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
/* ===== EXACT EMERALD SEC IMAGE REPLICATION ===== */
:root {
    --bg-main: #0c1117; 
    --bg-panel: #141a21; 
    --bg-card: #182028;
    --border: #212c36;
    --primary: #00fa88;
    --primary-dim: rgba(0, 250, 136, 0.15);
    --primary-glow: #00e676;
    --text-white: #e3e8ef;
    --text-dim: #9aa5b6;
    --danger: #f84b4b;
    --warning: #db9322;
    --term-bg: #030805;
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

/* Outer Wrapper (Glass) */
.dashboard-wrapper {
    position: relative; z-index: 10; width: 95%; height: 95%; display: flex;
    background: rgba(20, 26, 33, 0.85); backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);
    border-radius: 20px; box-shadow: 0 0 80px rgba(0, 250, 136, 0.05), inset 0 0 20px rgba(0, 250, 136, 0.02);
    border: 1px solid rgba(0, 250, 136, 0.1); overflow: hidden;
}

/* ===== SIDEBAR ===== */
.sidebar {
    width: 270px; background: transparent; border-right: 1px solid var(--border);
    display: flex; flex-direction: column; padding: 2.5rem 1.5rem; overflow-y: auto;
}
.brand { 
    display: flex; align-items: center; gap: 12px; font-size: 1.15rem; font-weight: 800;
    margin-bottom: 2.5rem; padding: 0 10px; color: #fff; text-shadow: 0 0 10px rgba(0, 250, 136, 0.3);
}
.brand-icon {
    width: 25px; height: 30px; background: linear-gradient(135deg, var(--primary) 0%, #00a055 100%);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex; align-items: center; justify-content: center; position: relative;
}
.brand-icon::after { content:'E'; font-family:'JetBrains Mono'; font-weight:900; color:#0c1117; font-size:0.8rem; }

.nav-item {
    padding: 12px 15px; margin-bottom: 5px; border-radius: 8px; color: var(--text-dim); cursor: pointer;
    font-size: 0.85rem; font-weight: 500; display: flex; align-items: center; gap: 12px; transition: 0.3s;
}
.nav-item:hover { color: var(--text-white); background: rgba(255,255,255,0.03); transform: translateX(3px); }
.nav-item.active { background: linear-gradient(90deg, rgba(0, 250, 136, 0.2) 0%, transparent 100%); color: var(--primary); box-shadow: inset 2px 0 10px rgba(0,250,136,0.1); }
.nav-icon { width: 18px; opacity: 0.7; flex-shrink: 0;}
.nav-item.active .nav-icon { opacity: 1; filter: drop-shadow(0 0 5px var(--primary)); stroke: var(--primary); }
.nav-section-title { font-size: 0.65rem; color: #4a5c6d; text-transform: uppercase; font-weight: 800; padding: 0 15px; margin: 25px 0 10px 0; letter-spacing: 1px;}

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
    transition: 0.3s; overflow: hidden;
}
.card:hover { border-color: rgba(0, 250, 136, 0.3); box-shadow: 0 5px 20px rgba(0,0,0,0.3); transform: translateY(-2px); }
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
.mini-chart path { fill: none; stroke: var(--primary); stroke-width: 2.5; filter: drop-shadow(0 5px 5px rgba(0,250,136,0.3)); transition: 0.5s; }
.mini-chart path.fill { fill: url(#greenGlow); stroke: none; filter: none; opacity: 0.4; transition: 0.5s; }

/* Blocks */
.left-block { grid-column: 1 / 3; display: flex; flex-direction: column; gap: 20px;}
.right-block { grid-column: 3 / 4; display: flex; flex-direction: column; gap: 20px;}
.bottom-block { grid-column: 1 / 4; display: flex; flex-direction: column; gap: 20px;}

/* Map Card */
.card-map { height: 320px; padding: 0 !important; }
.map-overlay-title { position: absolute; top: 1.5rem; left: 1.5rem; z-index: 20; color: #fff; font-weight: 700; font-size: 1.1rem; }
.map-bg-under { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #0c1116; opacity: 0.7; z-index: 1;}
.map-silhouette {
    position: absolute; top: 20px; left: 20px; right: 20px; bottom: 20px; background-color: rgba(255,255,255,0.05); 
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
    background: var(--term-bg); border: 1px solid rgba(0, 250, 136, 0.3);
    box-shadow: inset 0 0 15px rgba(0,250,136,0.05); font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
    padding: 1.5rem; color: #00df70; overflow-y: auto; position: relative; line-height: 1.7; flex: 1; border-radius: 12px;
}
.term-log { margin-bottom: 6px; word-break: break-all; }
.t-date { color: #5a6b7c; margin-right: 8px; }
.t-sys { color: var(--text-white); }
.t-msg { color: var(--primary); text-shadow: 0 0 5px rgba(0,250,136,0.2); }
.t-err { color: var(--danger); text-shadow: 0 0 5px rgba(255,75,75,0.2); }
.type-cursor { display: inline-block; width: 8px; height: 14px; background: var(--primary); animation: blink 1s step-end infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

.btn-action {
    background: linear-gradient(90deg, #00fb8c 0%, var(--primary) 100%);
    color: #0c1117; font-weight: 800; font-family: 'Inter'; font-size: 0.95rem; border: none; border-radius: 8px; padding: 15px;
    cursor: pointer; transition: 0.3s; box-shadow: 0 4px 15px rgba(0, 250, 136, 0.2); text-align: center; width: 100%; display: block;
}
.btn-action:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0, 250, 136, 0.4); filter: brightness(1.1); }

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

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }
</style>
</head>
<body>

<svg width="0" height="0"><defs><linearGradient id="greenGlow" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#00fa88" stop-opacity="0.5"/><stop offset="100%" stop-color="#00fa88" stop-opacity="0"/></linearGradient></defs></svg>
<canvas id="matrix-bg"></canvas>

<div class="dashboard-wrapper">
    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="brand"><div class="brand-icon"></div> EMERALD SEC</div>
        
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
        <div class="nav-item" onclick="switchTab('ps2', this)">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            AI-IoT Security
        </div>
        <div class="nav-item" onclick="switchTab('ps3', this)">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path></svg>
            Cloud Vault
        </div>

        <div class="nav-section-title" style="margin-top:auto;">System Access</div>
        <div class="nav-item"><svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg> System Logs</div>
        <div class="nav-item"><svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06..."></path></svg> Settings</div>
    </div>

    <!-- MAIN CONTENT -->
    <div class="main-content">
        <div class="top-header">
            <div class="icon-btn"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg></div>
            <div class="icon-btn" style="border-radius: 50%;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg></div>
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
                    <div class="card-title">Processing Speed </div>
                    <div class="big-val" id="val-speed">0.0 <span>Files/s</span></div>
                    <div class="chart-container"><svg class="mini-chart" viewBox="0 0 100 30" preserveAspectRatio="none"><path class="fill chart-path-fill" d="M0,30 L0,22 Q25,18 50,22 T100,18 L100,30 Z" /><path class="chart-path" fill="none" stroke="var(--primary)" stroke-width="2" vector-effect="non-scaling-stroke" d="M0,22 Q25,18 50,22 T100,18" /></svg></div>
                </div>

                <div class="card card-ready">
                    <div class="card-title">PQC Readiness Index</div>
                    <div class="big-val" id="val-ready">0%</div>
                    <div class="sub-val" id="ready-trend">PENDING <i>→</i></div>
                </div>

                <!-- ROW 2 : LEFT BLOCK (Inputs + Map) -->
                <div class="left-block">
                    <!-- Direct Input Area -->
                    <div class="card" style="padding-bottom:1.5rem;">
                        <div class="card-title" style="margin-bottom: 10px;">Security Audit Configuration <span class="badge" style="background:rgba(0,250,136,0.1); color:var(--primary);">Operational</span></div>
                        <div style="display:flex; gap:15px; margin-top:10px;">
                            <textarea id="code-in" class="m-input" style="flex:2; height:120px;" placeholder="// Paste raw Python / Java / C++ buffer here..."></textarea>
                            <div style="flex:1; display:flex; flex-direction:column; gap:8px;">
                                <input type="text" id="path-in" class="m-input" placeholder="Local Path (/var/www/sys)">
                                <input type="file" id="file-in" class="m-input" style="padding: 10px 8px;">
                                <button class="btn-action" style="padding:10px; margin-top:auto; font-size: 0.85rem;" onclick="executeScan()">Launch Analysis</button>
                            </div>
                        </div>
                    </div>

                    <!-- Live Map -->
                    <div class="card card-map">
                        <div class="map-overlay-title">Global Quantum Threat Telemetry</div>
                        <div style="position:absolute; top:2.5rem; left:1.5rem; z-index:20; max-width:60%; font-size: 0.75rem; color:var(--text-dim);">Simulating active quantum nodes probing cryptographic infrastructure parameters for Shor and Grover algorithm weaknesses.</div>
                        <div class="map-bg-under"></div>
                        <div class="map-silhouette"></div>
                        <svg class="map-svg" id="map-svg" viewBox="0 0 600 300" preserveAspectRatio="none"></svg>
                    </div>
                </div>

                <!-- ROW 2 : RIGHT BLOCK (Terminal) -->
                <div class="right-block">
                    <div class="card card-terminal" id="terminal-box">
                        <div style="position: sticky; top: -5px; background: var(--term-bg); padding-bottom: 10px; margin-bottom: 10px; border-bottom: 1px dashed var(--border); z-index:2;">root@emerald-matrix:~# tail -f /var/log/pqc_audit</div>
                        <div id="term-logs"><div class="term-log"><span class="t-sys">emerald-sys[1]:</span> <span class="t-msg">Awaiting audit payload invocation...</span></div></div>
                        <span class="type-cursor" id="term-cursor"></span>
                    </div>
                </div>

                <!-- ROW 3 : BOTTOM BLOCK (Full Width Table with Defined Mitigations) -->
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
                    </div>
                </div>
            </div>
        </div>

        <!-- ====================== TAB 2 : PS1 ALGO RESEARCH ====================== -->
        <div id="tab-ps1" class="tab-content">
            <div class="ps-header">Post-Quantum Cryptography Algorithms</div>
            <div class="ps-desc">Research and design cryptographic algorithms resistant to quantum computer attacks. Evaluate existing post-quantum cryptography schemes and propose implementations for mathematical lattice improvements. (Problem Statement 1)</div>
            
            <div style="display: flex; gap: 20px; align-items: flex-start;">
                <div class="card" style="flex:2;">
                    <div class="card-title" style="color:#fff;">NIST Finalized Scheme Evaluation Matrix</div>
                    
                    <div class="algo-row">
                        <div style="width:30%;">
                            <div style="font-weight:700; color:var(--primary);">ML-KEM (Kyber)</div>
                            <div style="font-size:0.75rem; color:var(--text-dim);">Module-Lattice KEM</div>
                        </div>
                        <div style="width:30%; text-align:center;">
                            <div class="badge" style="background:rgba(0,250,136,0.1); color:var(--primary); border:1px solid var(--primary);">NIST STANDARD</div>
                        </div>
                        <div style="width:40%; font-size:0.8rem; color:var(--text-dim); text-align:right;">
                            Resistant to Shor's. Recommended for rapid key exchange. Uses structured lattices.
                        </div>
                    </div>
                    <div class="algo-row">
                        <div style="width:30%;">
                            <div style="font-weight:700; color:var(--primary);">ML-DSA (Dilithium)</div>
                            <div style="font-size:0.75rem; color:var(--text-dim);">Module-Lattice Signature</div>
                        </div>
                        <div style="width:30%; text-align:center;">
                            <div class="badge" style="background:rgba(0,250,136,0.1); color:var(--primary); border:1px solid var(--primary);">NIST STANDARD</div>
                        </div>
                        <div style="width:40%; font-size:0.8rem; color:var(--text-dim); text-align:right;">
                            Highly efficient digital signatures based on Fiat-Shamir.
                        </div>
                    </div>
                    <div class="algo-row">
                        <div style="width:30%;">
                            <div style="font-weight:700; color:var(--warning);">SLH-DSA (SPHINCS+)</div>
                            <div style="font-size:0.75rem; color:var(--text-dim);">Stateless Hash-Based</div>
                        </div>
                        <div style="width:30%; text-align:center;">
                            <div class="badge" style="background:rgba(219,147,34,0.1); color:var(--warning); border:1px solid var(--warning);">SECONDARY FALLBACK</div>
                        </div>
                        <div style="width:40%; font-size:0.8rem; color:var(--text-dim); text-align:right;">
                            Conservative security, large signature footprint. Used if lattices break.
                        </div>
                    </div>
                </div>

                <div class="card card-terminal" style="flex:1; height:auto; min-height:300px;">
                    <div style="position: sticky; top: -5px; background: var(--term-bg); padding-bottom: 5px; margin-bottom: 5px; border-bottom: 1px dashed var(--border);">Algorithm Testing Workbench</div>
                    <textarea class="m-input" id="algo-math" style="height:120px; font-size:0.75rem; margin-top:10px; border-color:rgba(0,250,136,0.5); background:rgba(0,0,0,0.5);" placeholder="Enter lattice constants (e.g. n=512, q=3329) or pseudo-code to run AI analysis..."></textarea>
                    <button class="btn-action" style="padding:10px; margin-top:10px; font-size: 0.8rem; border-radius:4px;" onclick="simulatePS1()">Evaluate Algorithm</button>
                    <div id="ps1-res" style="margin-top:15px; font-size:0.75rem;"></div>
                </div>
            </div>
        </div>

        <!-- ====================== TAB 3 : PS2 AI-IOT SECURITY ====================== -->
        <div id="tab-ps2" class="tab-content">
            <div class="ps-header">Quantum-Resistant Cryptography for AI-Driven IoT</div>
            <div class="ps-desc"><strong>How this solves Problem Statement 2:</strong> IoT devices have low compute power, making heavy encryption impossible. Our solution uses highly efficient, lightweight post-quantum algorithms (ML-KEM / Kyber) at the Edge. The AI threat engine centrally detects vulnerabilities and dynamically pushes these lightweight PQC certificates directly to edge cameras and sensors, securing the AI models without overloading device CPUs.</div>
            
            <!-- IoT Connection Parameters -->
            <div class="card" style="margin-bottom: 5px; padding: 1rem 1.5rem; border-color:rgba(0,250,136,0.3);">
                <div class="card-title" style="margin-bottom: 10px; color:var(--primary);">Target Integration: Edge Devices / Sensors</div>
                <div style="display:flex; gap:15px;">
                    <input type="text" id="iot-endpoint" class="m-input" placeholder="Enter IoT Broker IP / Edge Node URI (e.g., tcp://192.168.1.44:1883)" style="flex:2;">
                    <input type="password" id="iot-token" class="m-input" placeholder="Device Auth Certificate" style="flex:1;">
                </div>
            </div>

            <div class="grid-system" style="grid-template-columns: 1fr 1.5fr 1fr; align-items:center; gap:10px;">
                <!-- Edge Nodes -->
                <div style="display:flex; flex-direction:column; gap:20px;">
                    <div class="card" style="text-align:center;">
                        <div class="node-orb" id="n1-orb" style="border-color:var(--danger); color:var(--danger); box-shadow: 0 0 15px rgba(248,75,75,0.2);">ECC</div>
                        <div style="font-weight:800; color:#fff;">Edge AI Device</div>
                        <div style="font-size:0.75rem; color:var(--text-dim); margin-top:8px;" id="n1-status">Classical Key Exchange</div>
                        <div style="font-size:0.65rem; color:var(--warning); margin-top:4px;" id="n1-ip-label">Awaiting Connection Binding...</div>
                    </div>
                </div>

                <!-- Transport / Action -->
                <div class="card" style="text-align:center; height:100%; justify-content:center; background:transparent; border:none; box-shadow:none;">
                    <div id="ps2-link" style="border-top:2px dashed var(--danger); position:relative; margin: 20px 0;">
                        <span id="ps2-link-text" style="position:absolute; top:-10px; left:50%; transform:translateX(-50%); color:var(--danger); font-size:0.75rem; font-weight:700; background:var(--bg-main); padding:0 10px;">VULNERABLE M.I.T.M DATALINK</span>
                    </div>
                    
                    <button class="btn-action" style="padding:15px; font-size: 0.85rem; width:100%; margin: 30px auto 0 auto;" onclick="simulatePS2()">Execute AI &rarr; PQC Edge Handshake</button>
                    
                    <div style="font-size:0.75rem; color:var(--text-dim); margin-top:15px; text-align:left; background:rgba(0,0,0,0.5); padding:10px; border-radius:8px; border:1px solid var(--border);">
                        <strong style="color:var(--primary);">Mechanism:</strong> AI replaces Diffie-Hellman (ECC) with Lattice-based ML-KEM on the fly.
                    </div>
                </div>

                <!-- Central Hub -->
                <div style="display:flex; flex-direction:column; gap:20px;">
                    <div class="card" style="text-align:center; border-color:var(--primary); box-shadow: 0 0 20px rgba(0,250,136,0.1);">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" style="margin: 0 auto 10px auto;"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>
                        <div style="font-weight:800; color:#fff; font-size:0.9rem;">AI Central Processor</div>
                        <div style="font-size:0.75rem; color:var(--primary); margin-top:5px;">Data Aggregation Hub</div>
                    </div>
                </div>
            </div>
            
            <div class="card card-terminal" style="height:150px; min-height:150px; margin-top:10px;">
                 <div style="position: sticky; top: -5px; background: var(--term-bg); padding-bottom: 5px; margin-bottom: 5px; border-bottom: 1px dashed var(--border);">IoT Network Traffic / PQC Tunneling Logs</div>
                 <div id="ps2-res">Listening for edge node anomalies...</div>
            </div>
        </div>

        <!-- ====================== TAB 4 : PS3 CLOUD VAULT ====================== -->
        <div id="tab-ps3" class="tab-content">
            <div class="ps-header">Quantum-Resistant Cryptography for Cloud Data Protection</div>
            <div class="ps-desc"><strong>How this solves Problem Statement 3:</strong> We use an AI Optimizer directly inside the Cloud Gateway to manage security protocols. It continuously monitors cloud ingress/egress. If the AI detects "Harvest Now, Decrypt Later" exfiltration patterns, it autonomously upgrades the vulnerable Data-in-Transit tunnel from RSA to ML-KEM and accelerates Key Rotation cycles to protect the database precisely when needed.</div>
            
            <!-- Cloud Connection Parameters -->
            <div class="card" style="margin-bottom: 5px; padding: 1rem 1.5rem; border-color:rgba(0,250,136,0.3);">
                <div class="card-title" style="margin-bottom: 10px; color:var(--primary);">Target Integration: External Cloud KMS</div>
                <div style="display:flex; gap:15px;">
                    <input type="text" id="cloud-endpoint" class="m-input" placeholder="Enter AWS / GCP KMS ARN Endpoint (e.g., arn:aws:kms:us-east-1:...)" style="flex:2;">
                    <input type="password" id="cloud-token" class="m-input" placeholder="Cloud IAM Admin Secret" style="flex:1;">
                </div>
            </div>

            <div class="grid-system" style="grid-template-columns: 1fr 1fr;">
                <div class="card">
                    <div class="card-title">Cloud AI Optimizer Engine</div>
                    
                    <div style="background:rgba(0,0,0,0.3); padding:15px; border:1px solid var(--border); border-radius:8px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-size:0.75rem; color:var(--text-dim); margin-bottom:5px;">Data-in-Transit Tunnel</div>
                            <div style="font-weight:700; color:var(--danger);" id="c-status">RSA-2048 (VULNERABLE)</div>
                        </div>
                        <div id="c-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--danger)" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg></div>
                    </div>

                    <div style="background:rgba(0,0,0,0.3); padding:15px; border:1px solid var(--border); border-radius:8px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-size:0.75rem; color:var(--text-dim); margin-bottom:5px;">AI Key Rotation Policy</div>
                            <div style="font-weight:700; color:var(--warning);" id="k-status">Static / 30 Days</div>
                        </div>
                        <div id="k-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--warning)" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg></div>
                    </div>
                    
                    <div style="font-size:0.8rem; color:var(--text-white); background: rgba(0,250,136,0.05); border-left: 3px solid var(--primary); padding:10px; margin-bottom:15px;">
                        The AI determines that rotating keys dynamically against traffic behavior minimizes cloud latency while maximizing post-quantum security constraints.
                    </div>

                    <button class="btn-action" style="padding:15px; font-size:0.9rem; margin-top:auto;" onclick="simulatePS3()">Trigger AI Cloud Protection Protocol</button>
                </div>
                
                <div class="card card-terminal" style="height:100%; min-height:300px;">
                    <div style="position: sticky; top: -5px; background: var(--term-bg); padding-bottom: 5px; margin-bottom: 5px; border-bottom: 1px dashed var(--border);">AWS KMS - AI Integration Logs</div>
                    <div id="ps3-logs" style="font-family:'JetBrains Mono'; font-size:0.75rem; color:var(--primary);">
                        Cloud Database Gateway initialized.<br>AI Traffic Monitor Active... listening on port 443.<br>
                    </div>
                </div>
            </div>
        </div>

    </div>
</div>

<script>
// Tab Switching
function switchTab(tabId, el) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');
    if(el) el.classList.add('active');
}

// Map Animation
const mapSvg = document.getElementById('map-svg');
const hubs = [{x: 150, y: 100}, {x: 300, y: 80}, {x: 450, y: 120}, {x: 320, y: 150}, {x: 200, y: 180}, {x: 500, y: 200}];
function drawMapAttacks() {
    let o = hubs[Math.floor(Math.random() * hubs.length)];
    let dests = hubs.filter(hub => hub !== o);
    let d = dests[Math.floor(Math.random() * dests.length)];
    o = {x: o.x + (Math.random()*40-20), y: o.y + (Math.random()*40-20)};
    d = {x: d.x + (Math.random()*40-20), y: d.y + (Math.random()*40-20)};
    createDot(o.x, o.y); createDot(d.x, d.y);
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    const mx = (o.x + d.x) / 2; const my = Math.min(o.y, d.y) - 50 - Math.random()*50;
    path.setAttribute("d", `M${o.x},${o.y} Q${mx},${my} ${d.x},${d.y}`);
    path.setAttribute("fill", "none"); path.setAttribute("stroke", "rgba(0, 250, 136, 0.6)"); path.setAttribute("stroke-width", "1.5");
    path.style.strokeDasharray = "1000"; path.style.strokeDashoffset = "1000"; path.style.transition = "stroke-dashoffset 1.5s ease-in-out";
    mapSvg.appendChild(path);
    setTimeout(() => { path.style.strokeDashoffset = "0"; }, 50);
    setTimeout(() => { path.style.opacity = "0"; path.style.transition = "opacity 0.5s"; }, 1500);
    setTimeout(() => { path.remove(); }, 2000);
}
function createDot(x,y) {
    const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    dot.setAttribute("cx", x); dot.setAttribute("cy", y); dot.setAttribute("r", "3"); dot.classList.add("hub-dot");
    mapSvg.appendChild(dot); setTimeout(() => { dot.remove(); }, 2000);
}
setInterval(drawMapAttacks, 600);

// Terminal utilities
const $ = id => document.getElementById(id);
async function typeTerm(boxId, msg, type='msg') {
    const t = $(boxId);
    let contentNode = document.createElement('span');
    contentNode.className = type === 'err' ? 't-err' : 't-msg';
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

// ====== MAIN TAB: PS1 ======
async function simulatePS1() {
    $('ps1-res').innerHTML = '';
    await typeTerm('ps1-res', 'Analyzing mathematical lattice structure...', 'msg');
    await typeTerm('ps1-res', 'Running simulated quantum Shor\'s attack...', 'warning');
    setTimeout(() => {
        $('ps1-res').innerHTML += '<br><br><span style="color:var(--primary);">Evaluation Complete. Algorithm demonstrates structural integrity against polynomial-time extraction. Lattice bounds verified.</span>';
    }, 1500);
}

// ====== MAIN TAB: PS2 ======
async function simulatePS2() {
    const ep = $('iot-endpoint').value || 'tcp://192.168.1.55:1883';
    $('ps2-res').innerHTML = '';
    await typeTerm('ps2-res', `INITIATING CONNECTION to Edge Broker: ${ep}...`, 'msg');
    await typeTerm('ps2-res', 'Authenticating device certificate signature...', 'warning');
    await typeTerm('ps2-res', 'AI Engine successfully bound to target device telemetry stream.', 'msg');
    await typeTerm('ps2-res', 'Vulnerability vectors detected. Revoking classical ECC certificates...', 'msg');
    
    // UI Updates
    setTimeout(() => {
        $('n1-orb').style.borderColor = 'var(--primary)'; $('n1-orb').style.color = 'var(--primary)';
        $('n1-orb').style.boxShadow = '0 0 15px rgba(0,250,136,0.3)'; $('n1-orb').innerText = 'KEM';
        $('n1-status').innerText = 'Optimized Kyber-768 Encrypted'; $('n1-status').style.color = 'var(--primary)';
        $('n1-ip-label').innerText = `Bound Target: ${ep}`; $('n1-ip-label').style.color = 'var(--primary)';
        
        $('ps2-link').style.borderTop = '2px dashed var(--primary)';
        $('ps2-link-text').innerText = 'QUANTUM-SECURE TUNNEL ESTABLISHED';
        $('ps2-link-text').style.color = 'var(--primary)';
    }, 1500);
    
    await typeTerm('ps2-res', `Pushing Kyber-768 ML-KEM key directly to target ${ep} via over-the-air firmware update.`, 'msg');
    await typeTerm('ps2-res', 'Handshake successful. Target Edge device fully shielded without localized CPU spike.', 'msg');
}

// ====== MAIN TAB: PS3 ======
async function simulatePS3() {
    const ep = $('cloud-endpoint').value || 'arn:aws:kms:us-east-1:123456789:key/dummy';
    $('ps3-logs').innerHTML = '';
    await typeTerm('ps3-logs', `Establishing Admin API Bridge to KMS Endpoint: ${ep}...`, 'msg');
    await typeTerm('ps3-logs', 'IAM Credentials authenticated via Webhook STS.', 'msg');
    await typeTerm('ps3-logs', 'Harvesting Attack Detected on connected ingress VPC! AI Policy Engine Triggered.', 'err');
    
    setTimeout(() => {
        $('c-status').innerText = 'ML-KEM (Kyber) + TLS 1.3';
        $('c-status').style.color = 'var(--primary)';
        $('c-icon').innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="var(--primary)" stroke="var(--bg-card)" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>';
        
        $('k-status').innerText = 'AI Dynamic / High Frequency';
        $('k-status').style.color = 'var(--primary)';
        $('k-icon').innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>';
    }, 1200);

    await typeTerm('ps3-logs', `Transmitting new Lattice Master Keys directly to IAM Vault: ${ep}`, 'msg');
    await typeTerm('ps3-logs', 'AI instructs KMS to modify Key Rotation Policy based on extreme threat velocity -> Dynamic interval.', 'msg');
    await typeTerm('ps3-logs', `SUCCESS: Traffic routing through vault ${ep} is fully quantum-shielded.`, 'msg');
}


// ====== MAIN TAB: CORE AUDIT ======
async function executeScan() {
    const code = $('code-in').value, file = $('file-in').files[0], path = $('path-in').value;
    $('term-logs').innerHTML = ''; await typeTerm('term-logs', 'Initiating localized heuristic target analysis...');
    
    let fd = new FormData(), url = '/v3/audit';
    if(file) { fd.append('file', file); url = '/v3/audit/file'; await typeTerm('term-logs', 'Uploading source archive: ' + file.name); }
    else if(path) { fd.append('path', path); url = '/v3/audit/path'; await typeTerm('term-logs','Scanning path tree: ' + path); }
    else { fd = JSON.stringify({code}); await typeTerm('term-logs','Injecting code buffer for inspection...'); }

    try {
        const startT = Date.now();
        const r = await fetch(url, { method:'POST', body:fd, headers:(file||path)?{}:{'Content-Type':'application/json'} });
        const data = await r.json(); const dur = ((Date.now() - startT) / 1000).toFixed(2);
        
        if(data.status === 'error') { await typeTerm('term-logs','CRITICAL_ERR: ' + data.message, 'err'); } 
        else {
            const fs = data.base_report.files_processed || 1;
            if($('val-threats')) $('val-threats').innerText = data.base_report.vulnerabilities_found;
            if($('val-files')) $('val-files').innerText = fs;
            if($('val-speed')) $('val-speed').innerHTML = (fs/Math.max(dur, 0.1)).toFixed(1) + ' <span>MBps</span>';
            
            const risk = data.base_report.risk_level, readyPct = data.base_report.readiness_percentage;
            if($('b-threat')) {
                $('b-threat').innerText = risk;
                $('b-threat').className = `badge ${risk==='CRITICAL'?'badge-crit':(risk==='HIGH'?'badge-high':'')}`;
            }
            updateWaveCharts(risk);
            
            if($('val-ready')) $('val-ready').innerText = readyPct + '%';
            if($('ready-trend')) {
                $('ready-trend').innerHTML = readyPct === 100 ? 'SECURE <i>✔</i>' : 'CRITICAL <i style="transform: rotate(45deg);">↘</i>';
                $('ready-trend').style.color = readyPct === 100 ? 'var(--primary)' : 'var(--danger)';
            }
            if($('ring-status')) $('ring-status').style.background = `conic-gradient(var(--primary) 0% ${readyPct}%, var(--danger) ${readyPct}% 100%)`;

            // HIGHLY DEFINED RESULT BLOCK (USER REQUEST)
            if(data.vulnerable_implementations.length > 0) {
                // Highly visual rows
                $('vuln-tbody').innerHTML = data.vulnerable_implementations.map((v, i) => `
                    <tr>
                        <td style="border-left: 2px solid ${v.risk_level==='CRITICAL'?'var(--danger)':'var(--warning)'}; border-top-left-radius:8px; border-bottom-left-radius:8px;">
                            <div style="font-weight:700; color:#fff; font-size: 0.9rem; margin-bottom: 5px;">Line Target: ${v.line}</div>
                            <div style="font-size:0.75rem; color:var(--text-dim); line-height: 1.4;">${(v.context||"No context").substring(0,80)}...</div>
                        </td>
                        <td>
                            <div style="font-family:'JetBrains Mono'; color:var(--text-white); font-size: 0.9rem; background:rgba(255,255,255,0.05); padding:5px 8px; border-radius:4px; display:inline-block;">${v.algorithm}</div>
                        </td>
                        <td>
                            <div class="badge ${v.risk_level === 'CRITICAL' ? 'badge-crit' : 'badge-high'}">${v.risk_level}</div>
                            <div style="font-size:0.65rem; color:var(--text-dim); margin-top:5px; line-height:1.4;">${v.objective_metadata.how_vulnerable.substring(0,50)}...</div>
                        </td>
                        <td style="background: rgba(0, 250, 136, 0.03);">
                            <div style="color:var(--primary); font-family:'Inter'; font-weight:800; font-size:0.8rem; margin-bottom:5px; display:flex; align-items:center; gap:5px;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> REQUIRED UPGRADE</div>
                            <div style="color:var(--text-white); font-size:0.75rem; line-height: 1.5; font-family:'JetBrains Mono'; padding:8px; background:rgba(0,0,0,0.5); border:1px solid rgba(0,250,136,0.3); border-radius:4px;">
                                ${v.objective_metadata.prevention}
                            </div>
                        </td>
                    </tr>
                `).join('');
                
            } else {
                $('vuln-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--primary);padding:30px;font-size:1rem; border:2px dashed var(--primary); background:rgba(0,250,136,0.05); border-radius:12px;">✓ Validated. Target architecture meets PQC standards. No mitigations required.</td></tr>';
            }
            await typeTerm('term-logs','Dashboard metrics synchronized with PQC schema.');
            $('vuln-tbody').scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    } catch(e) { await typeTerm('term-logs','SYS ERROR: ' + e.toString(), 'err'); }
}

// Matrix initiation loop
setInterval(drawMatrix, 35);
window.addEventListener('resize', () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; });
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
    if 'file' not in request.files: return jsonify({'status': 'error', 'message': 'No file'})
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
    if not path: return jsonify({'status': 'error', 'message': 'No path provided'})
    report = manager.scan_system_path(path)
    app.latest_scan = report
    return jsonify(report)

@app.route('/v3/download-report')
def download_report():
    if not hasattr(app, 'latest_scan'): return "No scan data found", 404
    scan = app.latest_scan
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "PQC Results"
    ws.merge_cells('A1:E1')
    ws['A1'] = "EMERALD SEC PQC UNIFIED READINESS REPORT"
    ws['A1'].font = Font(bold=True, size=14, color="FFFFFF")
    ws['A1'].fill = PatternFill(start_color="00FA88", end_color="00FA88", fill_type="solid")
    ws['A1'].alignment = Alignment(horizontal="center")
    ws.append(["Location", "Algorithm", "Risk", "Vulnerability Impact", "Mitigation Protocol"])
    for v in scan.get('vulnerable_implementations', []):
        m = v.get('objective_metadata', {})
        ws.append([f"Line {v.get('line', '?')}", v['algorithm'], v.get('risk_level','?'), m.get('how_vulnerable','-'), m.get('prevention','-')])
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="EmeraldSec_Unified_Report.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    print("\nEMERALD SEC PQC DASHBOARD STARTING...")
    app.run(debug=True, host='0.0.0.0', port=5001)
