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
    <title>SafeGuard-Env | DevSecOps Evaluator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #000000; --panel: #111111; --border: #333333; --text: #EDEDED; --muted: #A1A1AA; --accent: #3b82f6; --success: #22c55e; }
        body { margin: 0; padding: 0; font-family: 'Inter', sans-serif; background-color: var(--bg); color: var(--text); background-image: radial-gradient(#222 1px, transparent 1px); background-size: 24px 24px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { width: 100%; max-width: 800px; padding: 2rem; }
        h1 { font-size: 2.5rem; font-weight: 600; letter-spacing: -0.05em; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 12px; }
        .status-dot { width: 12px; height: 12px; background: var(--success); border-radius: 50%; box-shadow: 0 0 12px var(--success); }
        .subtitle { color: var(--muted); font-size: 1.1rem; margin-bottom: 3rem; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        .card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; }
        .card h3 { font-size: 1rem; font-weight: 500; margin-bottom: 1rem; color: #fff; }
        ul { list-style: none; padding: 0; margin: 0; }
        ul li { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 12px; color: var(--muted); font-size: 0.95rem; line-height: 1.5; }
        ul li::before { content: '→'; color: var(--border); }
        .code-block { font-family: 'JetBrains Mono', monospace; background: #000; padding: 1rem; border-radius: 6px; border: 1px solid var(--border); font-size: 0.85rem; color: #e5e7eb; margin-top: 1rem; }
        .code-block .keyword { color: #c678dd; }
        .code-block .string { color: #98c379; }
        .actions { margin-top: 3rem; display: flex; gap: 1rem; }
        .btn { padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 500; text-decoration: none; font-size: 0.9rem; transition: all 0.2s; }
        .btn-primary { background: #fff; color: #000; }
        .btn-primary:hover { background: #e5e5e5; }
        .btn-secondary { background: transparent; color: #fff; border: 1px solid var(--border); }
        .btn-secondary:hover { background: var(--panel); }
    </style>
</head>
<body>
    <div class="container">
        <h1><div class="status-dot"></div> SafeGuard-Env</h1>
        <p class="subtitle">Headless Enterprise Zero-Knowledge Environment for API Key Leak Evaluation via OpenEnv</p>
        
        <div class="grid">
            <div class="card">
                <h3>Architecture Context</h3>
                <ul>
                    <li>AES-256-GCM Secure In-Memory States</li>
                    <li>Procedural VFS Auto-Generation (Level 3)</li>
                    <li>Markovian Compute Cost Agent Mechanics</li>
                    <li>Honeypot Decoy Verification Systems</li>
                </ul>
            </div>
            <div class="card">
                <h3>API Endpoints</h3>
                <div class="code-block">
                    <div><span class="keyword">POST</span> <span class="string">/reset</span> : Init Simulation</div>
                    <div style="margin-top: 0.5rem;"><span class="keyword">POST</span> <span class="string">/step</span>  : Execute Agent Action</div>
                    <div style="margin-top: 0.5rem;"><span class="keyword">POST</span> <span class="string">/grade</span> : Terminal State Reward</div>
                </div>
            </div>
        </div>

        <div class="actions">
            <a href="/redoc" class="btn btn-primary" target="_top">View API Specifications</a>
            <a href="https://github.com/mainti5-crypto/SAFEGUARD-ENV" class="btn btn-secondary" target="_top">View Source Code</a>
        </div>
    </div>
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
