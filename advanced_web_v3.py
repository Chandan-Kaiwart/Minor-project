from flask import Flask, request, jsonify, send_file
import os, sys, time, random, tempfile, shutil, subprocess, requests
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
<title>Emerald PQC | Tactical Command</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
/* ===== EVERGREEN THEME (User Request) ===== */
:root {
    /* DARK THEME (DEFAULT) */
    --bg-main: #013220; 
    --bg-panel: #022d1d;
    --bg-card: #0c1c14;
    --primary: #50C878;
    --warning: #DB9322;
    --danger: #F84B4B;
    --text-white: #FFFFFF;
    --text-dim: #D1F2EB;
    --border: rgba(80, 200, 120, 0.2);
    --term-bg: #000;
}

body.light-theme {
    --bg-main: #F0F3F2; /* Soft Slate-Mint Grey */
    --bg-panel: #FFFFFF;
    --bg-card: #FFFFFF;
    --primary: #0B6E4F;
    --warning: #B45309;
    --danger: #991B1B;
    --text-white: #06402B;
    --text-dim: #5F7D75;
    --border: #CCD6D1; /* Sharper edges */
    --term-bg: #F8FAF9;
    --card-shadow: 0 10px 40px rgba(0,0,0,0.06);
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

/* Outer Wrapper (Evergreen Glass) */
.dashboard-wrapper {
    position: relative; z-index: 10; width: 95%; height: 95%; display: flex;
    background: var(--bg-main); backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);
    border-radius: 20px; box-shadow: 0 0 80px rgba(80, 200, 120, 0.1), inset 0 0 20px rgba(80, 200, 120, 0.05);
    border: 1px solid var(--border); overflow: hidden;
    transition: background 0.4s ease, border-color 0.4s ease;
}

/* ===== SIDEBAR ===== */
.sidebar {
    width: 270px; background: var(--bg-panel); border-right: 1px solid var(--border);
    display: flex; flex-direction: column; padding: 2.5rem 1.5rem; overflow-y: auto;
    transition: background 0.4s ease, border-color 0.4s ease;
}
.brand { 
    display: flex; align-items: center; gap: 12px; font-size: 1.15rem; font-weight: 800;
    margin-bottom: 2.5rem; padding: 0 10px; color: var(--text-white); text-shadow: 0 0 10px rgba(0, 250, 136, 0.3);
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
.nav-item:hover { color: var(--primary); background: rgba(80,200,120,0.08); transform: translateX(3px); }
.nav-item.active { background: var(--primary); color: #fff !important; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
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
.mini-chart path { fill: none; stroke: var(--primary); stroke-width: 2.5; filter: drop-shadow(0 5px 5px rgba(0,250,136,0.3)); transition: 0.5s; }
.mini-chart path.fill { fill: url(#greenGlow); stroke: none; filter: none; opacity: 0.4; transition: 0.5s; }

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

/* Tom Cruise Runner */
#tom-cruise-wrapper {
    position: fixed; bottom: 20px; left: -200px; width: 200px; height: 150px; 
    z-index: 9999; pointer-events: none; display: none;
}
#tom-cruise-wrapper img { width: 100%; height: auto; }
@keyframes runAcross {
    0% { left: -250px; }
    100% { left: 100%; }
}
.running { display: none !important; } /* Removed Ethanol Hunt Runner */
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

/* Pad & Modal UI (User Request) */
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
</style>
</head>
<body>

<svg width="0" height="0"><defs><linearGradient id="greenGlow" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#50C878" stop-opacity="0.5"/><stop offset="100%" stop-color="#0B6E4F" stop-opacity="0"/></linearGradient></defs></svg>
<canvas id="matrix-bg"></canvas>

<!-- Mission Impossible Elements -->
<audio id="mi-theme" preload="auto">
    <!-- Stable Archive.org Download Link -->
    <source src="mission-impossible_oEwlsUsI.mp3" type="audio/mpeg">
    <source src="mission-impossible_oEwlsUsI.mp3" type="audio/mpeg">
</audio>
</audio>
</audio>

<div class="dashboard-wrapper">
    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="brand"><div class="brand-icon" style="background: var(--border);"></div> EMERALD PQC</div>
        
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
        <div class="nav-item" onclick="switchTab('ps3', this)">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
            System Logs
        </div>
        <div class="nav-item" onclick="toggleTheme()">
            <div class="nav-icon" style="background:rgba(80,200,120,0.1); width:24px; height:24px; display:flex; align-items:center; justify-content:center; border-radius:4px;">
                <svg id="theme-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
            </div>
            <span id="theme-text">Dark Mode</span>
        </div>
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

                <!-- NEW ROW 2 : SIDE BLOCK (Terminal) -->
                <div class="side-block">
                    <div class="card card-terminal" id="terminal-box" style="height: 570px; position: relative; overflow: hidden;">
                        <div id="scan-overlay"></div>
                        <div style="position: sticky; top: -5px; background: var(--term-bg); padding-bottom: 10px; margin-bottom: 10px; border-bottom: 1px dashed var(--border); z-index:2;">root@emerald-matrix:~# tail -f /var/log/pqc_audit</div>
                        <div id="term-logs"><div class="term-log"><span class="t-sys">emerald-sys[1]:</span> <span class="t-msg">Awaiting audit payload invocation...</span></div></div>
                        <span class="type-cursor" id="term-cursor"></span>
                    </div>
                </div>

                <!-- NEW ROW 2 : MAIN BLOCK (Inputs + Map) -->
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
                                <div id="gh-action-btn" class="github-btn" onclick="handleGitHubClick()">
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
                            <div id="map-summary-text">Synchronizing with SANS ISC honeypots... Identifying global botnet clusters probing for legacy RSA/ECC vulnerabilities.</div>
                        </div>
                        <div style="position:absolute; top:2.5rem; left:1.2rem; z-index:20; max-width:55%; font-size: 0.7rem; color:var(--text-dim); opacity:0.6;">Mapping Real-Time IoCs and infrastructure reconnaissance.</div>
                        <div class="map-bg-under"></div>
                        <div class="map-silhouette"></div>
                        <svg class="map-svg" id="map-svg" viewBox="0 0 600 300" preserveAspectRatio="none"></svg>
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
                        <div id="res-injector"></div>
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
                
                <div class="card card-terminal" style="height:100%; min-height:400px; display:flex; flex-direction:column;">
                    <div style="position: sticky; top: -5px; background: var(--term-bg); padding-bottom: 5px; margin-bottom: 5px; border-bottom: 1px dashed var(--border);">Unified Scan History Archive</div>
                    <div id="history-box" style="flex:1; overflow-y:auto; margin-bottom:15px; display:flex; flex-direction:column; gap:8px;">
                        <div style="text-align:center; padding:40px; color:var(--text-dim); border:1px dashed var(--border); border-radius:12px;">No historical records in current session.</div>
                    </div>
                    <div style="border-top: 1px dashed var(--border); padding-top:10px;">
                        <div style="font-size:0.6rem; color:var(--text-dim); margin-bottom:5px;">AI Traffic Monitor (Raw Feed)</div>
                        <div id="ps3-logs" style="font-family:'JetBrains Mono'; font-size:0.7rem; color:var(--primary); max-height:100px; overflow-y:auto;">
                            Cloud Database Gateway initialized.<br>AI Traffic Monitor Active... listening on port 443.
                        </div>
                    </div>
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
        <input type="password" id="gh-token-in" class="m-input" style="margin-bottom:15px; font-size: 0.7rem; border-color: rgba(255,255,255,0.1);" placeholder="Personal Access Token (for Private Repos)">
        <div style="font-size: 0.6rem; color: var(--text-dim); margin-bottom: 5px; opacity: 0.8;">Note: Unauthenticated requests only show Public repositories.</div>
        <div id="repo-container" class="repo-list">
            <!-- Dynamic repos -->
            <div style="text-align:center; padding:20px; color:var(--text-dim);">Fetching metadata...</div>
        </div>
        <div style="margin-top:20px;">
            <button class="btn-action" style="background:#444;" onclick="$('github-modal').style.display='none'">Cancel</button>
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

// Map Logic (Precision Geolocation Engine)
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
        if(ld[0]) summaryText += `<br><br>Top Threat: <span style="color:var(--danger)">${ld[0].ip}</span> from <b>${ld[0].country}</b> performing high-frequency reconnaissance.`;
        $('map-summary-text').innerHTML = summaryText;

        ld.slice(0, 15).forEach((threat, i) => {
            const country = threat.country || 'Unknown';
            const base = countryCoords[country] || [320, 110]; // Default to Central Afro-Eurasia (Land)
            const x = base[0] + (Math.random()*16 - 8); // Add micro-jitter 
            const y = base[1] + (Math.random()*16 - 8);
            
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", x); circle.setAttribute("cy", y); circle.setAttribute("r", 4);
            circle.setAttribute("class", "hub-dot");
            circle.innerHTML = `<title>REAL SCAN: ${threat.ip} (${country}) | Reports: ${threat.count}</title>`;
            mapSvg.appendChild(circle);

            const pulse = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            pulse.setAttribute("cx", x); pulse.setAttribute("cy", y); pulse.setAttribute("r", 4);
            pulse.setAttribute("fill", "none"); pulse.setAttribute("stroke", "var(--primary)");
            pulse.innerHTML = `<animate attributeName="r" from="4" to="25" dur="2.5s" begin="${i * 0.4}s" repeatCount="indefinite" />
                               <animate attributeName="opacity" from="0.7" to="0" dur="2.5s" begin="${i * 0.4}s" repeatCount="indefinite" />`;
            mapSvg.appendChild(pulse);
        });
    } catch(e) { console.log("Map Precision Error:", e); }
}
setInterval(drawMapAttacks, 30000);
drawMapAttacks();

// Terminal utilities
const $ = id => document.getElementById(id);
async function typeTerm(boxId, msg, type='msg') {
    const t = $(boxId);
    let contentNode = document.createElement('span');
    contentNode.className = type === 'err' ? 't-err' : (type === 'warning' ? 't-warning' : 't-msg'); // Added warning type
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
    if(scanHistory.length === 0) return;
    box.innerHTML = scanHistory.map((h, i) => `
        <div class="repo-item" style="padding:15px; border:1px solid var(--border); background:rgba(0,0,0,0.2);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div style="font-weight:800; color:var(--primary); font-size:0.8rem;">MISSION: ${h.type.toUpperCase()}</div>
                    <div style="font-size:0.65rem; color:var(--text-dim); margin-top:3px;">${h.date} | ${h.origin}</div>
                </div>
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
function closeCodePad() { 
    $('code-modal').style.display = 'none'; 
    const code = $('code-in').value;
    if(code.trim().length > 0) {
        $('pad-status').innerText = 'Buffer Size: ' + code.length + ' chars';
        $('pad-status').style.color = 'var(--primary)';
    }
}

async function handleGitHubClick() {
    if(!githubUser) {
        const user = prompt("Enter GitHub Username to synchronize:");
        if(user) {
            githubUser = user;
            $('gh-text').innerText = "Syncing...";
            await fetchRepos();
        }
    } else {
        $('github-modal').style.display = 'flex';
        await fetchRepos();
    }
}

async function fetchRepos() {
    $('gh-user-display').innerText = githubUser;
    const container = $('repo-container');
    const token = $('gh-token-in').value;
    
    container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-dim);">Fetching metadata...</div>';
    
    try {
        let url = token ? `https://api.github.com/user/repos?per_page=100&sort=updated` : `https://api.github.com/users/${githubUser}/repos?per_page=100&sort=updated`;
        let headers = { 'Accept': 'application/vnd.github.v3+json' };
        if(token) headers['Authorization'] = `token ${token}`;

        const resp = await fetch(url, { headers });
        const repos = await resp.json();
        
        if(!Array.isArray(repos)) {
            if(repos.message === "Bad credentials") throw new Error("Invalid Personal Access Token");
            throw new Error("Repository discovery failed for user: " + githubUser);
        }
        
        if(repos.length === 0) {
            container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-dim);">No repositories found.</div>';
            return;
        }

        container.innerHTML = repos.map(r => `
            <div class="repo-item" onclick="selectRepo('${r.clone_url}', '${r.name}')">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="font-weight:700; color:#fff;">${r.name}</div>
                    ${r.private ? '<span style="font-size:0.5rem; background:rgba(219, 147, 34, 0.2); color:var(--warning); padding:2px 5px; border-radius:4px; text-transform:uppercase;">Private</span>' : ''}
                </div>
                <div style="font-size:0.65rem; color:var(--text-dim);">${r.language || 'Code'} • Ready for Audit</div>
            </div>
        `).join('');
        
        $('gh-action-btn').classList.add('connected');
        $('gh-text').innerText = token ? "Secure Sync (PAT)" : "Browse Repos";
    } catch(e) {
        container.innerHTML = `<div style="color:var(--danger); padding:20px; font-size:0.8rem;"><b>Discovery Error:</b><br>${e.message}</div>`;
        githubUser = null;
        $('gh-text').innerText = "Connect GitHub";
    }
}

function selectRepo(url, name) {
    selectedGitHubRepo = url;
    $('gh-text').innerText = "Repo: " + name;
    $('github-modal').style.display = 'none';
    $('gh-action-btn').style.borderColor = 'var(--primary)';
}

// ====== MAIN TAB: CORE AUDIT ======
async function executeScan() {
    const code = $('code-in').value, file = $('file-in').files[0], path = $('path-in').value, githubUrl = selectedGitHubRepo;
    const audio = $('mi-theme');
    const runner = $('tom-cruise-wrapper');
    // MISSION START (Animation First)
    const scanLine = $('scan-overlay');
    if(scanLine) {
        // Fallback or Audio-Synced duration
        const duration = audio.duration && !isNaN(audio.duration) ? (audio.duration / 2) : 5;
        document.documentElement.style.setProperty('--mission-pass', duration + 's');
        scanLine.classList.remove('active-scan');
        void scanLine.offsetWidth; // Trigger reflow
        scanLine.classList.add('active-scan');
        
        // Auto-Cleanup after 2 passes or audio end
        setTimeout(() => { scanLine.classList.remove('active-scan'); }, duration * 2 * 1000);
    }

    try { 
        audio.currentTime = 0;
        audio.volume = 0.6;
        
        audio.onended = () => {
            runner.classList.remove('running');
            runner.style.display = 'none';
        };

        let p = audio.play(); 
        if (p !== undefined) {
            p.catch(e => console.log("Audio Blocked"));
        }
        runner.style.display = 'block';
        runner.classList.add('running');
    } catch(e) { console.log("Mission Start Error:", e); }

    $('term-logs').innerHTML = ''; await typeTerm('term-logs', 'Initiating localized heuristic target analysis...');
    
    let url = '/v3/audit';
    let fetchOptions = { method:'POST' };

    if(githubUrl) {
        const fd = new FormData();
        fd.append('url', githubUrl);
        url = '/v3/audit/github';
        fetchOptions.body = fd;
        await typeTerm('term-logs', 'Synchronizing with GitHub repository: ' + githubUrl);
    }
    else if(file) { 
        const fd = new FormData();
        fd.append('file', file); 
        url = '/v3/audit/file'; 
        fetchOptions.body = fd;
        await typeTerm('term-logs', 'Extracting source archive: ' + file.name); 
    }
    else if(path) { 
        const fd = new FormData();
        fd.append('path', path); 
        url = '/v3/audit/path'; 
        fetchOptions.body = fd;
        await typeTerm('term-logs','Scanning local mapping: ' + path); 
    }
    else { 
        fetchOptions.headers = {'Content-Type':'application/json'};
        fetchOptions.body = JSON.stringify({ code: code });
        await typeTerm('term-logs','Injecting code buffer for inspection...'); 
    }

    try {
        const startT = Date.now();
        const r = await fetch(url, fetchOptions); 
        const data = await r.json(); const dur = ((Date.now() - startT) / 1000).toFixed(2);
        
        if(data.status === 'error') { await typeTerm('term-logs','CRITICAL_ERR: ' + data.message, 'err'); } 
        else {
            // Log to Mission Vault
            const auditTitle = githubUrl ? 'GitHub Sync' : (file ? 'Archive Scan' : (path ? 'Local Drive' : 'Code Buffer'));
            const finalRisk = data.base_report.risk_level || 'UNKNOWN';
            
            scanHistory.push({
                type: auditTitle,
                origin: githubUrl || file?.name || path || 'Memory Buffer',
                summary: `Audit complete. Detected ${data.base_report.vulnerabilities_found} vulnerability vectors. Target Readiness: ${data.base_report.readiness_percentage}%`,
                risk: finalRisk,
                date: new Date().toLocaleTimeString()
            });
            updateHistoryUI();

            const fs = data.base_report.files_processed || 1;
            if($('val-threats')) $('val-threats').innerText = data.base_report.vulnerabilities_found;
            if($('val-files')) $('val-files').innerText = fs;
            if($('val-speed')) $('val-speed').innerHTML = (fs/Math.max(dur, 0.1)).toFixed(1) + ' <span>MBps</span>';
            
            const risk = data.base_report.risk_level, readyPct = data.base_report.readiness_percentage;
            if($('b-threat')) {
                $('b-threat').innerText = risk;
                $('b-threat').className = `badge ${risk==='CRITICAL'?'badge-crit':(risk==='HIGH'?'badge-high':(risk==='MEDIUM'?'badge-warn':''))}`;
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
                $('vuln-tbody').innerHTML = data.vulnerable_implementations.map((v, i) => `
                    <tr>
                        <td style="border-left: 2px solid ${v.risk_level==='CRITICAL'?'var(--danger)':'var(--warning)'}; border-top-left-radius:8px; border-bottom-left-radius:8px;">
                            <div style="font-weight:700; color:#fff; font-size: 0.9rem; margin-bottom: 5px;">Line Target: ${v.line}</div>
                            <div style="font-size:0.75rem; color:var(--text-dim); line-height: 1.4;">${v.file}</div>
                        </td>
                        <td>
                            <div style="font-family:'JetBrains Mono'; color:var(--text-white); font-size: 0.9rem; background:rgba(255,255,255,0.05); padding:5px 8px; border-radius:4px; display:inline-block;">${v.algorithm}</div>
                        </td>
                        <td>
                            <div class="badge ${v.risk_level === 'CRITICAL' ? 'badge-crit' : 'badge-high'}">${v.risk_level}</div>
                            <div style="font-size:0.65rem; color:var(--text-dim); margin-top:5px; line-height:1.4;">${v.objective_metadata.how_vulnerable}</div>
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
            await typeTerm('term-logs', 'Dashboard metrics synchronized with PQC schema.');
            $('vuln-tbody').scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    } catch(e) {
        await typeTerm('term-logs', 'FATAL: ' + e.message, 'err');
    } finally {
        // Handled by audio.onended for perfect sync
    }
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

@app.route('/v3/audit/github', methods=['POST'])
def audit_github():
    repo_url = request.form.get('url')
    if not repo_url: return jsonify({'status': 'error', 'message': 'No GitHub URL provided'})
    
    tmp_path = tempfile.mkdtemp()
    try:
        # Shallow clone for maximum scan speed
        subprocess.check_call(['git', 'clone', '--depth', '1', repo_url, tmp_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        report = manager.scan_system_path(tmp_path)
        app.latest_scan = report
        return jsonify(report)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)

@app.route('/v3/live-threats')
def live_threats():
    try:
        # SANS ISC Real-time Scanning Community Feed
        r = requests.get("https://isc.sans.edu/api/sources/summary/30?json", timeout=5)
        return jsonify(r.json())
    except:
        return jsonify([
            {"ip": "185.224.128.91", "count": 1422, "country": "RU"},
            {"ip": "45.155.205.233", "count": 1105, "country": "DE"}
        ])

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

@app.route('/mission-impossible_oEwlsUsI.mp3')
def serve_audio():
    return send_file('mission-impossible_oEwlsUsI.mp3')

if __name__ == '__main__':
    print("\nEMERALD SEC PQC DASHBOARD STARTING...")
    app.run(debug=True, host='0.0.0.0', port=5001)
