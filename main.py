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
    <title>SafeGuard-Env API</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --bg-color: #0b0f19; --card-bg: rgba(255, 255, 255, 0.03); --card-border: rgba(255, 255, 255, 0.08); --text-primary: #f8fafc; --text-secondary: #94a3b8; --accent-glow: rgba(56, 189, 248, 0.4); }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background-color: var(--bg-color); color: var(--text-primary); display: flex; align-items: center; justify-content: center; height: 100vh; overflow: hidden; position: relative; }
        .orb { position: absolute; width: 600px; height: 600px; border-radius: 50%; filter: blur(100px); opacity: 0.4; z-index: -1; animation: float 15s ease-in-out infinite alternate; }
        .orb-1 { top: -200px; left: -100px; background: radial-gradient(circle, rgba(56,189,248,0.3) 0%, rgba(11,15,25,0) 70%); }
        .orb-2 { bottom: -200px; right: -100px; background: radial-gradient(circle, rgba(139,92,246,0.3) 0%, rgba(11,15,25,0) 70%); animation-delay: -5s; }
        @keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(50px, 30px) scale(1.1); } }
        .glass-card { background: var(--card-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--card-border); border-radius: 24px; padding: 4rem 3rem; max-width: 600px; width: 90%; text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); transform: translateY(20px); opacity: 0; animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        @keyframes slideUp { to { transform: translateY(0); opacity: 1; } }
        .badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.2); color: #4ade80; padding: 6px 16px; border-radius: 9999px; font-size: 0.875rem; font-weight: 600; margin-bottom: 2rem; letter-spacing: 0.5px; text-transform: uppercase; }
        .pulse-dot { width: 8px; height: 8px; background-color: #4ade80; border-radius: 50%; box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7); animation: pulse 2s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(74, 222, 128, 0); } 100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); } }
        h1 { font-size: 3.5rem; font-weight: 800; line-height: 1.1; margin-bottom: 1.5rem; background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 50%, #94a3b8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px; }
        .accent { background: linear-gradient(135deg, #38bdf8 0%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        p { font-size: 1.125rem; color: var(--text-secondary); line-height: 1.7; margin-bottom: 2.5rem; font-weight: 300; }
        .btn { display: inline-block; background: linear-gradient(135deg, #0ea5e9, #4f46e5); color: white; text-decoration: none; padding: 1rem 2.5rem; border-radius: 9999px; font-weight: 600; font-size: 1.125rem; transition: all 0.3s ease; box-shadow: 0 4px 15px var(--accent-glow); position: relative; overflow: hidden; }
        .btn::after { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0)); opacity: 0; transition: opacity 0.3s ease; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px var(--accent-glow); }
        .btn:hover::after { opacity: 1; }
    </style>
</head>
<body>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="glass-card">
        <div class="badge"><div class="pulse-dot"></div>System Online</div>
        <h1>SafeGuard-<span class="accent">Env</span></h1>
        <p>You have reached the headless OpenEnv API gateway. This architecture provides zero-knowledge cryptographic evaluation for DevSecOps AI agents under Reinforcement Learning topologies.</p>
        <a href="/docs" class="btn">Launch API Matrix</a>
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
