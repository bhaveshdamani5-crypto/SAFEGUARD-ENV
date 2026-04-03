import os
import requests
from openai import OpenAI
import json
from typing import List, Optional

API_KEY = os.environ.get("HF_TOKEN") or os.environ.get("API_KEY", "dummy")
API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
BENCHMARK = "safeguard_env"
ENV_URL = "http://localhost:7860"

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def run_task_level(level: int):
    task_name = f"level_{level}"
    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)
    
    client = OpenAI(
        api_key=API_KEY,
        base_url=API_BASE_URL if API_BASE_URL else None
    )

    try:
        reset_res = requests.post(f"{ENV_URL}/reset", params={"level": level})
        reset_res.raise_for_status()
        obs = reset_res.json()
    except Exception as e:
        log_step(step=0, action="reset", reward=0.0, done=True, error=str(e))
        log_end(success=False, steps=0, score=0.0, rewards=[])
        return

    current_text = obs["text"]
    steps_taken = 0
    rewards = []
    
    for step in range(1, 4): # max 3 turns
        steps_taken = step
        prompt = f"""
        You are an AI Data Compliance Officer checking PII in: "{current_text}"
        Provide start_index, end_index (exclusive), and a label.
        Format exclusively as JSON object: {{"start_index": int, "end_index": int, "label": "string"}}
        If no more secrets exist, return {{"done": true}}
        """
        
        action_payload = {}
        error_val = None
        reward_val = 0.0
        done_val = False
        action_str = ""

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            action_data = json.loads(response.choices[0].message.content)
            action_str = json.dumps(action_data).replace('"', "'")
            
            if action_data.get("done"):
                done_val = True
                log_step(step=step, action=action_str, reward=0.0, done=True, error=None)
                rewards.append(0.0)
                break
                
            action_payload = {
                "start_index": int(action_data.get("start_index", -1)),
                "end_index": int(action_data.get("end_index", -1)),
                "label": action_data.get("label", "ERR")
            }
            
            step_res = requests.post(f"{ENV_URL}/step", json=action_payload)
            step_res.raise_for_status()
            step_out = step_res.json()
            
            reward_val = step_out['reward']
            done_val = step_out['done']
            
            log_step(step=step, action=action_str, reward=reward_val, done=done_val, error=None)
            rewards.append(reward_val)
            
            if done_val:
                break
                
        except Exception as e:
            error_val = str(e).replace('"', "'").replace('\n', ' ')
            log_step(step=step, action=action_str if action_str else "error", reward=0.0, done=True, error=error_val)
            rewards.append(0.0)
            break
            
    # Grade the episode
    try:
        grade_res = requests.post(f"{ENV_URL}/grade")
        grade_out = grade_res.json()
        score = grade_out['score']
        success = score >= 0.5 # Example threshold
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    except Exception as e:
        log_end(success=False, steps=steps_taken, score=0.0, rewards=rewards)

if __name__ == "__main__":
    for lvl in [1, 2, 3]:
        run_task_level(lvl)
