from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from models import Observation, Action, StepResult, StateResponse, GraderResult
from env import SafeGuardEnv
import uuid
from typing import Optional, Dict

app = FastAPI(
    title="SafeGuard-Env (DevSecOps Edition)", 
    description="Zero-Knowledge Data Compliance Environment for evaluating API Key & PII redaction capabilities.", 
    version="2.0.0"
)

# Concurrency Management: Store unique environment states per session
sessions: Dict[str, SafeGuardEnv] = {}

def get_env(session_id: str) -> SafeGuardEnv:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired. Please call /reset first.")
    return sessions[session_id]

@app.get("/", response_class=HTMLResponse)
def root_page():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SafeGuard-Env | Zero-Knowledge DevSecOps Evaluator</title>
    <meta name="description" content="Enterprise-grade Zero-Knowledge Data Compliance Environment for evaluating AI agents on API Key & PII redaction with AES-256-GCM cryptography.">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg: #050508;
            --surface: rgba(255,255,255,0.03);
            --glass: rgba(255,255,255,0.05);
            --glass-border: rgba(255,255,255,0.08);
            --text: #f0f0f5;
            --text-muted: #8b8b9e;
            --accent: #6366f1;
            --accent-glow: rgba(99,102,241,0.4);
            --success: #10b981;
            --success-glow: rgba(16,185,129,0.5);
            --warning: #f59e0b;
            --danger: #ef4444;
            --cyan: #06b6d4;
            --pink: #ec4899;
        }

        @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-12px); } }
        @keyframes pulse-dot { 0%, 100% { box-shadow: 0 0 8px var(--success-glow); } 50% { box-shadow: 0 0 24px var(--success-glow), 0 0 48px var(--success-glow); } }
        @keyframes gradient-shift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        @keyframes fade-up { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes scan-line { 0% { top: -2px; } 100% { top: 100%; } }
        @keyframes typing { from { width: 0; } to { width: 100%; } }
        @keyframes blink { 50% { border-color: transparent; } }
        @keyframes orbit { from { transform: rotate(0deg) translateX(180px) rotate(0deg); } to { transform: rotate(360deg) translateX(180px) rotate(-360deg); } }
        @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        /* Animated background */
        .bg-grid {
            position: fixed; inset: 0; z-index: 0;
            background-image:
                linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px);
            background-size: 60px 60px;
        }
        .bg-glow {
            position: fixed; z-index: 0;
            width: 600px; height: 600px;
            border-radius: 50%;
            filter: blur(120px);
            opacity: 0.15;
            pointer-events: none;
        }
        .bg-glow-1 { top: -200px; left: -100px; background: var(--accent); }
        .bg-glow-2 { bottom: -200px; right: -100px; background: var(--cyan); }
        .bg-glow-3 { top: 40%; left: 50%; transform: translate(-50%, -50%); background: var(--pink); opacity: 0.06; width: 800px; height: 800px; }

        .page { position: relative; z-index: 1; }

        /* HERO */
        .hero {
            min-height: 85vh;
            display: flex; flex-direction: column;
            justify-content: center; align-items: center;
            text-align: center;
            padding: 2rem;
            animation: fade-up 0.8s ease-out;
        }
        .badge {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 6px 16px;
            background: rgba(99,102,241,0.1);
            border: 1px solid rgba(99,102,241,0.2);
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 500;
            color: var(--accent);
            margin-bottom: 2rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        .badge .dot {
            width: 8px; height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse-dot 2s ease-in-out infinite;
        }
        .hero h1 {
            font-size: clamp(3rem, 6vw, 5rem);
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.05;
            margin-bottom: 1.5rem;
        }
        .hero h1 .gradient-text {
            background: linear-gradient(135deg, #6366f1 0%, #06b6d4 40%, #ec4899 70%, #6366f1 100%);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradient-shift 6s ease-in-out infinite;
        }
        .hero .subtitle {
            font-size: 1.2rem;
            color: var(--text-muted);
            max-width: 650px;
            line-height: 1.7;
            margin-bottom: 2.5rem;
        }
        .hero-actions { display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; }

        .btn {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            text-decoration: none;
            font-size: 0.95rem;
            transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
            cursor: pointer;
            border: none;
            position: relative;
            overflow: hidden;
        }
        .btn-primary {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: #fff;
            box-shadow: 0 4px 24px rgba(99,102,241,0.3);
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(99,102,241,0.5);
        }
        .btn-secondary {
            background: var(--glass);
            color: #fff;
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(16px);
        }
        .btn-secondary:hover {
            background: rgba(255,255,255,0.08);
            border-color: rgba(255,255,255,0.15);
            transform: translateY(-2px);
        }
        .btn-outline {
            background: transparent;
            color: var(--accent);
            border: 1px solid rgba(99,102,241,0.3);
        }
        .btn-outline:hover {
            background: rgba(99,102,241,0.1);
            border-color: rgba(99,102,241,0.5);
            transform: translateY(-2px);
        }
        .btn svg { width: 18px; height: 18px; }

        /* STATS BAR */
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 3rem;
            padding: 2rem;
            margin-top: 3rem;
            animation: fade-up 1s ease-out 0.3s both;
        }
        .stat { text-align: center; }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            background: linear-gradient(135deg, var(--accent), var(--cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .stat-label { font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.1em; }

        /* SECTIONS */
        .section {
            max-width: 1200px;
            margin: 0 auto;
            padding: 6rem 2rem;
        }
        .section-header {
            text-align: center;
            margin-bottom: 4rem;
        }
        .section-header h2 {
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin-bottom: 1rem;
        }
        .section-header p { color: var(--text-muted); font-size: 1.05rem; max-width: 550px; margin: 0 auto; line-height: 1.6; }

        /* FEATURE CARDS */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
        }
        .feature-card {
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
            transition: all 0.4s cubic-bezier(0.4,0,0.2,1);
            position: relative;
            overflow: hidden;
        }
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            opacity: 0;
            transition: opacity 0.3s;
        }
        .feature-card:hover {
            border-color: rgba(99,102,241,0.2);
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        .feature-card:hover::before { opacity: 1; }
        .feature-icon {
            width: 48px; height: 48px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 1.2rem;
        }
        .feature-icon.purple { background: rgba(99,102,241,0.15); }
        .feature-icon.cyan { background: rgba(6,182,212,0.15); }
        .feature-icon.pink { background: rgba(236,72,153,0.15); }
        .feature-icon.green { background: rgba(16,185,129,0.15); }
        .feature-icon.amber { background: rgba(245,158,11,0.15); }
        .feature-card h3 { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem; }
        .feature-card p { color: var(--text-muted); font-size: 0.9rem; line-height: 1.6; }

        /* ARCHITECTURE */
        .arch-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            align-items: start;
        }
        .arch-flow {
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
        }
        .flow-step {
            display: flex; align-items: center; gap: 16px;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.75rem;
            transition: all 0.3s;
            position: relative;
        }
        .flow-step:hover { background: rgba(255,255,255,0.03); }
        .flow-step:not(:last-child)::after {
            content: '';
            position: absolute;
            left: 27px; bottom: -6px;
            width: 2px; height: 12px;
            background: linear-gradient(180deg, var(--accent), transparent);
        }
        .flow-num {
            width: 36px; height: 36px;
            border-radius: 10px;
            background: rgba(99,102,241,0.15);
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 0.85rem;
            color: var(--accent);
            flex-shrink: 0;
        }
        .flow-text h4 { font-size: 0.95rem; font-weight: 600; margin-bottom: 2px; }
        .flow-text span { font-size: 0.8rem; color: var(--text-muted); }

        /* CODE TERMINAL */
        .terminal {
            background: #0a0a0f;
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            overflow: hidden;
        }
        .terminal-header {
            display: flex; align-items: center; gap: 8px;
            padding: 12px 16px;
            background: rgba(255,255,255,0.03);
            border-bottom: 1px solid var(--glass-border);
        }
        .terminal-dot { width: 10px; height: 10px; border-radius: 50%; }
        .terminal-dot.red { background: #ef4444; }
        .terminal-dot.yellow { background: #f59e0b; }
        .terminal-dot.green { background: #10b981; }
        .terminal-title { color: var(--text-muted); font-size: 0.75rem; margin-left: auto; font-family: 'JetBrains Mono', monospace; }
        .terminal-body {
            padding: 1.5rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            line-height: 1.8;
            color: #a0a0b8;
            min-height: 280px;
        }
        .terminal-body .prompt { color: var(--success); }
        .terminal-body .cmd { color: #e5e7eb; }
        .terminal-body .comment { color: #4a4a5e; }
        .terminal-body .key { color: #c678dd; }
        .terminal-body .val { color: #98c379; }
        .terminal-body .url { color: var(--cyan); }
        .terminal-body .warn { color: var(--warning); }
        .terminal-body .info { color: var(--accent); }

        /* API ENDPOINTS */
        .api-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
        .api-card {
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 14px;
            padding: 1.5rem;
            transition: all 0.3s;
        }
        .api-card:hover {
            border-color: rgba(99,102,241,0.2);
            transform: translateY(-3px);
        }
        .api-method {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .api-method.post { background: rgba(99,102,241,0.15); color: var(--accent); }
        .api-method.get { background: rgba(16,185,129,0.15); color: var(--success); }
        .api-path {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.15rem;
            font-weight: 600;
            margin: 0.75rem 0 0.5rem;
            color: var(--text);
        }
        .api-desc { font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; }

        /* TOOLS SECTION */
        .tool-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        .tool-chip {
            display: flex; align-items: center; gap: 10px;
            padding: 14px 18px;
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            transition: all 0.3s;
        }
        .tool-chip:hover { border-color: rgba(99,102,241,0.2); transform: scale(1.02); }
        .tool-chip .icon { font-size: 1.2rem; }
        .tool-chip .name { font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 0.85rem; }
        .tool-chip .desc { font-size: 0.75rem; color: var(--text-muted); }

        /* CTA */
        .cta-section {
            text-align: center;
            padding: 6rem 2rem;
            position: relative;
        }
        .cta-section::before {
            content: '';
            position: absolute;
            top: 0; left: 50%; transform: translateX(-50%);
            width: 600px; height: 1px;
            background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
        }
        .cta-actions { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; margin-top: 2rem; }

        /* FOOTER */
        .footer {
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            font-size: 0.8rem;
            border-top: 1px solid var(--glass-border);
        }
        .footer a { color: var(--accent); text-decoration: none; }
        .footer a:hover { text-decoration: underline; }

        /* RESPONSIVE */
        @media (max-width: 768px) {
            .arch-container { grid-template-columns: 1fr; }
            .stats-bar { gap: 1.5rem; flex-wrap: wrap; }
            .hero h1 { font-size: 2.5rem; }
        }

        /* SCROLL ANIMATIONS */
        .reveal {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.7s cubic-bezier(0.4,0,0.2,1);
        }
        .reveal.visible {
            opacity: 1;
            transform: translateY(0);
        }
    </style>
</head>
<body>

<div class="bg-grid"></div>
<div class="bg-glow bg-glow-1"></div>
<div class="bg-glow bg-glow-2"></div>
<div class="bg-glow bg-glow-3"></div>

<div class="page">

    <!-- HERO -->
    <section class="hero">
        <div class="badge">
            <span class="dot"></span>
            Live on OpenEnv
        </div>
        <h1>
            <span class="gradient-text">SafeGuard-Env</span>
        </h1>
        <p class="subtitle">
            Enterprise-grade Zero-Knowledge evaluation environment for AI agents.
            Test redaction precision against AES-256-GCM encrypted secrets, honeypot decoys, and procedurally generated filesystems.
        </p>
        <div class="hero-actions">
            <a href="/docs" class="btn btn-primary" target="_top">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"/></svg>
                Interactive API Docs
            </a>
            <a href="/redoc" class="btn btn-secondary" target="_top">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/></svg>
                API Reference
            </a>
            <a class="btn btn-outline" onclick="document.getElementById('repo-section').scrollIntoView({behavior:'smooth'})" style="cursor:pointer;">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5"/></svg>
                Explore Architecture
            </a>
        </div>

        <div class="stats-bar">
            <div class="stat">
                <div class="stat-value">AES-256</div>
                <div class="stat-label">GCM Encryption</div>
            </div>
            <div class="stat">
                <div class="stat-value">∞</div>
                <div class="stat-label">Procedural Levels</div>
            </div>
            <div class="stat">
                <div class="stat-value">5</div>
                <div class="stat-label">Agent Tools</div>
            </div>
            <div class="stat">
                <div class="stat-value">0</div>
                <div class="stat-label">State Leakage</div>
            </div>
        </div>
    </section>

    <!-- FEATURES -->
    <section class="section reveal" id="features">
        <div class="section-header">
            <h2>Why SafeGuard-Env?</h2>
            <p>Built for serious AI security evaluation — not another toy environment.</p>
        </div>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon purple">🔐</div>
                <h3>Zero-Knowledge Architecture</h3>
                <p>All secrets encrypted in-memory with AES-256-GCM via Python's cryptography library. No plaintext leakage, ever.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon cyan">🌀</div>
                <h3>Infinite Procedural Levels</h3>
                <p>Level 3 generates randomized filesystems with unique secrets and honeypots on every reset — solving RL overfitting.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon pink">🍯</div>
                <h3>Honeypot Decoy System</h3>
                <p>Deploys contextual mock keys and test accounts to benchmark hallucination rates against legitimate redaction.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon green">⚡</div>
                <h3>Enterprise Concurrency</h3>
                <p>UUID-based session isolation enables parallel agent evaluations without state leakage or race conditions.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon amber">💰</div>
                <h3>Compute Cost Mechanics</h3>
                <p>Search operations cost reward points, forcing agents to strategically balance exploration vs. targeted redaction.</p>
            </div>
        </div>
    </section>

    <!-- ARCHITECTURE -->
    <section class="section reveal" id="repo-section">
        <div class="section-header">
            <h2>Architecture & Flow</h2>
            <p>How the evaluation pipeline processes each agent session.</p>
        </div>
        <div class="arch-container">
            <div class="arch-flow">
                <div class="flow-step">
                    <div class="flow-num">1</div>
                    <div class="flow-text">
                        <h4>POST /reset</h4>
                        <span>Initialize session with UUID. Load encrypted VFS scenario.</span>
                    </div>
                </div>
                <div class="flow-step">
                    <div class="flow-num">2</div>
                    <div class="flow-text">
                        <h4>Agent Explores</h4>
                        <span>list_directory, read_file, search_filesystem tools.</span>
                    </div>
                </div>
                <div class="flow-step">
                    <div class="flow-num">3</div>
                    <div class="flow-text">
                        <h4>AES-256 Decrypt</h4>
                        <span>File contents decrypted on-the-fly from memory vault.</span>
                    </div>
                </div>
                <div class="flow-step">
                    <div class="flow-num">4</div>
                    <div class="flow-text">
                        <h4>Agent Redacts</h4>
                        <span>redact_file tool replaces secrets. Honeypots await.</span>
                    </div>
                </div>
                <div class="flow-step">
                    <div class="flow-num">5</div>
                    <div class="flow-text">
                        <h4>POST /grade</h4>
                        <span>Precision, Recall, F1 score + honeypot penalty calculation.</span>
                    </div>
                </div>
            </div>

            <div class="terminal">
                <div class="terminal-header">
                    <div class="terminal-dot red"></div>
                    <div class="terminal-dot yellow"></div>
                    <div class="terminal-dot green"></div>
                    <span class="terminal-title">safeguard-env — session</span>
                </div>
                <div class="terminal-body">
                    <div><span class="comment"># Initialize a new evaluation session</span></div>
                    <div><span class="prompt">$</span> <span class="cmd">curl -X POST /reset?level=1</span></div>
                    <div><span class="info">→</span> <span class="val">session_id: "a3f8..."</span></div>
                    <div style="margin-top: 0.5rem;"><span class="comment"># Explore the virtual filesystem</span></div>
                    <div><span class="prompt">$</span> <span class="cmd">tool: list_directory {path: "/"}</span></div>
                    <div><span class="info">→</span> .env/  app/  src/</div>
                    <div style="margin-top: 0.5rem;"><span class="prompt">$</span> <span class="cmd">tool: read_file {path: "/.env"}</span></div>
                    <div><span class="info">→</span> STRIPE_API_KEY=<span class="warn">sk_live_51Ma...</span></div>
                    <div style="margin-top: 0.5rem;"><span class="comment"># Redact the real secret</span></div>
                    <div><span class="prompt">$</span> <span class="cmd">tool: redact_file {path: "/.env", secret: "sk_live_..."}</span></div>
                    <div><span class="val">✓ Redacted successfully (+0.5 reward)</span></div>
                    <div style="margin-top: 0.5rem;"><span class="comment"># Grade the session</span></div>
                    <div><span class="prompt">$</span> <span class="cmd">curl -X POST /grade</span></div>
                    <div><span class="val">✓ Score: 1.00 | Precision: 1.00 | Recall: 1.00</span></div>
                </div>
            </div>
        </div>
    </section>

    <!-- API ENDPOINTS -->
    <section class="section reveal">
        <div class="section-header">
            <h2>API Endpoints</h2>
            <p>OpenEnv-compliant REST API for agent evaluation.</p>
        </div>
        <div class="api-grid">
            <div class="api-card">
                <span class="api-method post">POST</span>
                <div class="api-path">/reset</div>
                <p class="api-desc">Initialize a new evaluation session. Optionally specify level (1-3) for scenario difficulty.</p>
            </div>
            <div class="api-card">
                <span class="api-method post">POST</span>
                <div class="api-path">/step</div>
                <p class="api-desc">Execute an agent action with tool_name and arguments. Returns observation, reward, and done state.</p>
            </div>
            <div class="api-card">
                <span class="api-method get">GET</span>
                <div class="api-path">/state</div>
                <p class="api-desc">Retrieve current decrypted VFS state and accumulated reward for debugging and inspection.</p>
            </div>
            <div class="api-card">
                <span class="api-method post">POST</span>
                <div class="api-path">/grade</div>
                <p class="api-desc">Compute terminal evaluation: Precision, Recall, F1 score with honeypot penalty deductions.</p>
            </div>
        </div>
    </section>

    <!-- AGENT TOOLS -->
    <section class="section reveal">
        <div class="section-header">
            <h2>Agent Toolbox</h2>
            <p>Five specialized tools available to the AI agent during evaluation.</p>
        </div>
        <div class="tool-list">
            <div class="tool-chip">
                <span class="icon">📂</span>
                <div>
                    <div class="name">list_directory</div>
                    <div class="desc">Browse VFS directory tree</div>
                </div>
            </div>
            <div class="tool-chip">
                <span class="icon">📄</span>
                <div>
                    <div class="name">read_file</div>
                    <div class="desc">Decrypt & read file contents</div>
                </div>
            </div>
            <div class="tool-chip">
                <span class="icon">🔍</span>
                <div>
                    <div class="name">search_filesystem</div>
                    <div class="desc">Query all files (costs -0.05)</div>
                </div>
            </div>
            <div class="tool-chip">
                <span class="icon">✂️</span>
                <div>
                    <div class="name">redact_file</div>
                    <div class="desc">Replace secrets in files</div>
                </div>
            </div>
            <div class="tool-chip">
                <span class="icon">🏁</span>
                <div>
                    <div class="name">submit</div>
                    <div class="desc">End session & auto-grade</div>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA -->
    <section class="cta-section reveal">
        <h2 style="font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 0.75rem;">Ready to Evaluate?</h2>
        <p style="color: var(--text-muted); font-size: 1.05rem; max-width: 500px; margin: 0 auto;">
            Explore the interactive API documentation or browse the full source code.
        </p>
        <div class="cta-actions">
            <a href="/docs" class="btn btn-primary" target="_top">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5"/></svg>
                Open Swagger UI
            </a>
            <a href="/redoc" class="btn btn-secondary" target="_top">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"/></svg>
                ReDoc Reference
            </a>
            <a href="javascript:void(0);" class="btn btn-outline" id="view-repo-btn" target="_top">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5"/></svg>
                View Repository
            </a>
        </div>
    </section>

    <footer class="footer">
        <p>SafeGuard-Env v2.5.0 — Built for the <a href="https://huggingface.co/OpenEnv" target="_blank">Meta OpenEnv Hackathon</a> 🛡️</p>
    </footer>

</div>

<script>
    // Scroll reveal animations
    const reveals = document.querySelectorAll('.reveal');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    reveals.forEach(el => observer.observe(el));

    // View Repository button: try to detect HF Space URL and link to Files tab
    (function() {
        const btn = document.getElementById('view-repo-btn');
        if (btn) {
            // On HuggingFace Spaces, window.location will be the space URL
            // We need to link to the Files tab of the same space
            const loc = window.location;
            const hfMatch = loc.hostname.match(/^(.+)\\.hf\\.space$/);
            if (hfMatch) {
                // Running on HF Spaces subdomain (e.g. bhavesh657-safeguard-env.hf.space)
                const parts = hfMatch[1].split('-');
                const username = parts[0];
                const spaceName = parts.slice(1).join('-');
                btn.href = 'https://huggingface.co/spaces/' + username + '/' + spaceName + '/tree/main';
                btn.target = '_blank';
            } else if (loc.hostname === 'huggingface.co' || loc.hostname.endsWith('.huggingface.co')) {
                // Embedded in HF iframe
                btn.href = loc.pathname.replace(/\\/$/, '') + '/tree/main';
                btn.target = '_top';
            } else {
                // Local development — link to HuggingFace space directly
                btn.href = 'https://huggingface.co/spaces/bhavesh657/SafeGuard-Env/tree/main';
                btn.target = '_blank';
            }
        }
    })();
</script>

</body>
</html>"""

@app.post("/reset", response_model=Observation)
def reset_env(level: Optional[int] = None, session_id: Optional[str] = None):
    # Support backward compatibility by using default session mapping if clients omit session_id
    sid = session_id if session_id else str(uuid.uuid4())
    sessions[sid] = SafeGuardEnv(session_id=sid)
    return sessions[sid].reset(level)

@app.post("/step", response_model=StepResult)
def step_env(action: Action, session_id: Optional[str] = None):
    # Action object now contains session_id, fallback to query param or default
    sid = action.session_id if action.session_id != "default" else (session_id if session_id else "default")
    env = get_env(sid)
    return env.step(action)

@app.get("/state", response_model=StateResponse)
def state_env(session_id: str = "default"):
    env = get_env(session_id)
    return env.state()

@app.post("/grade", response_model=GraderResult)
def grade_env(session_id: str = "default"):
    env = get_env(session_id)
    return env.grade()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860)
