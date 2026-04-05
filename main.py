from fastapi import FastAPI, HTTPException
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
