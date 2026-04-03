from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Observation(BaseModel):
    document_id: str
    text: str
    level: int

class Action(BaseModel):
    start_index: int
    end_index: int
    label: str

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
    cleaned_text: str
    current_reward: float
