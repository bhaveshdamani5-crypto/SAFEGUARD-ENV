from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Observation(BaseModel):
    session_id: str = "default"
    task_description: str
    tool_output: str
    level: int

class Action(BaseModel):
    session_id: str = "default"
    tool_name: str
    arguments: Dict[str, Any]

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]

class GraderResult(BaseModel):
    precision: float
    recall: float
    score: float # float between 0.0 and 1.0
    reward: float

class StateResponse(BaseModel):
    cleaned_vfs_state: Dict[str, Any]
    current_reward: float
