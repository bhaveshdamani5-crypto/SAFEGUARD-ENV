from fastapi import FastAPI
from models import Observation, Action, StepResult, StateResponse, GraderResult
from env import env_instance

app = FastAPI(title="SafeGuard-Env", description="AI Data compliance Meta OpenEnv framework interface", version="1.0.0")

from typing import Optional

@app.post("/reset", response_model=Observation)
def reset_env(level: Optional[int] = None):
    return env_instance.reset(level)

@app.post("/step", response_model=StepResult)
def step_env(action: Action):
    return env_instance.step(action)

@app.get("/state", response_model=StateResponse)
def state_env():
    return env_instance.state()

@app.post("/grade", response_model=GraderResult)
def grade_env():
    return env_instance.grade()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860)
