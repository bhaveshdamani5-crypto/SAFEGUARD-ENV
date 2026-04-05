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
    return """
    <html>
        <head>
            <title>SafeGuard-Env API</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background-color: #0f172a; color: #f8fafc; margin: 0; }
                h1 { color: #38bdf8; font-size: 3rem; margin-bottom: 0.5rem; }
                p { font-size: 1.25rem; max-width: 600px; text-align: center; color: #94a3b8; line-height: 1.6; }
                .btn { margin-top: 2rem; padding: 1rem 2rem; background-color: #0284c7; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1rem; transition: background-color 0.2s; }
                .btn:hover { background-color: #0369a1; }
            </style>
        </head>
        <body>
            <h1>🛡️ SafeGuard-Env</h1>
            <p>Welcome to the <strong>SafeGuard-Env OpenEnv API</strong>. This is a headless Reinforcement Learning environment designed for DevSecOps AI Agent evaluation.</p>
            <p><strong>System Status:</strong> <span style="color:#22c55e">Online & Active</span></p>
            <a href="/docs" class="btn">View OpenEnv API Documentation</a>
        </body>
    </html>
    """

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
