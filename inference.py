import os
import requests
from openai import OpenAI
import json
from typing import List, Optional

API_KEY = os.environ.get("HF_TOKEN") or os.environ.get("API_KEY", "dummy")
API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
BENCHMARK = "safeguard_env_v2"
ENV_URL = "http://localhost:7860"

def log_start(task: str, env: str, model: str) -> None:
    print(f"\n[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, thought: str, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP {step}] Thought: {thought}\n  Action: {action}\n  Reward: {reward:.2f} Done: {done_val} Error: {error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} sum_reward={sum(rewards):.2f}\n", flush=True)

def run_task_level(level: int):
    task_name = f"level_{level}"
    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)
    
    client = None
    if API_KEY and API_KEY.lower() != "dummy":
        client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE_URL if API_BASE_URL else None
        )
    elif level == 3:
        print("  --> Skipping Level 3 (Procedural infinite mode is purely for live LLM agents with API Keys, not Mock Agents)")
        return

    try:
        reset_res = requests.post(f"{ENV_URL}/reset", params={"level": level})
        reset_res.raise_for_status()
        obs = reset_res.json()
        session_id = obs.get("session_id", "default")
    except Exception as e:
        print(f"Failed to reset env: {e}")
        return

    task_desc = obs["task_description"]
    system_prompt = f"""You are an autonomous DevSecOps agent investigating a filesystem leak.
Your task: {task_desc}

You have access to a Virtual Filesystem.
Available tools:
1. "list_directory": {{"path": "<string>"}} - Lists files/folders in a directory.
2. "read_file": {{"path": "<string>"}} - Returns the content of a file.
3. "search_filesystem": {{"query": "<string>"}} - Recursively searches all files for a string. Computes at a cost of -0.05 reward.
4. "redact_file": {{"path": "<string>", "secret": "<exact_string_to_hide>", "replacement": "***"}} - Replaces secret text in a file.
5. "submit": {{}} - Complete the task.

At each step, you MUST respond strictly in this JSON format:
{{
    "thought": "Your reasoning about what to do next based on the last tool output",
    "tool_name": "name_of_tool_to_run",
    "arguments": {{"key": "value"}}
}}
Do NOT output markdown (NO ```json). Output raw object.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Session started.\nObservation: {obs['tool_output']}"}
    ]
    
    steps_taken = 0
    rewards = []
    
    # HARDCODED Dummy answers depending on the scenario level
    # Used only if client is absent (Zero Friction Demo Mode)
    dummy_actions_level_1 = [
        {"thought": "I should list the root directory to find suspicious files.", "tool_name": "list_directory", "arguments": {"path": "/"}},
        {"thought": "There is a .env file. I should read it.", "tool_name": "read_file", "arguments": {"path": "/.env"}},
        {"thought": "Found the live stripe key in .env. I must redact it.", "tool_name": "redact_file", "arguments": {"path": "/.env", "secret": "sk_live_51Mabcde12345", "replacement": "***"}},
        {"thought": "I should also check app/config.py.", "tool_name": "read_file", "arguments": {"path": "/app/config.py"}},
        {"thought": "That key says MOCK. The instructions told me not to redact mock keys. I am done.", "tool_name": "submit", "arguments": {}}
    ]
    
    dummy_actions_level_2 = [
        {"thought": "I need to look for log files where PII might have leaked.", "tool_name": "list_directory", "arguments": {"path": "/logs/"}},
        {"thought": "There is an auth.log file. I'll read it.", "tool_name": "read_file", "arguments": {"path": "/logs/auth.log"}},
        {"thought": "Found realuser@gmail.com in the logs. Redacting.", "tool_name": "redact_file", "arguments": {"path": "/logs/auth.log", "secret": "realuser@gmail.com", "replacement": "***"}},
        {"thought": "I should check tests for any other files.", "tool_name": "list_directory", "arguments": {"path": "/tests/"}},
        {"thought": "Found mocks.json, reading it.", "tool_name": "read_file", "arguments": {"path": "/tests/mocks.json"}},
        {"thought": "That is an automation user, which the incident report told me to ignore. I am done.", "tool_name": "submit", "arguments": {}}
    ]

    dummy_sequence = dummy_actions_level_1 if level == 1 else dummy_actions_level_2
    
    for step in range(1, 15):
        steps_taken = step
        
        try:
            if client:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    response_format={"type": "json_object"}
                )
                action_data = json.loads(response.choices[0].message.content)
            else:
                # Dummy execution mode
                if step - 1 < len(dummy_sequence):
                    action_data = dummy_sequence[step - 1]
                else:
                    action_data = {"thought": "Out of steps.", "tool_name": "submit", "arguments": {}}
                
            thought = action_data.get("thought", "")
            tool_name = action_data.get("tool_name", "error")
            arguments = action_data.get("arguments", {})
            action_str = f"{tool_name}({arguments})"
            
            action_payload = {
                "session_id": session_id,
                "tool_name": tool_name,
                "arguments": arguments
            }
            
            step_res = requests.post(f"{ENV_URL}/step", json=action_payload)
            step_res.raise_for_status()
            step_out = step_res.json()
            
            reward_val = step_out['reward']
            done_val = step_out['done']
            tool_output = step_out['observation']['tool_output']
            
            # Use info dict for the terminal StepResult (OpenEnv integration)
            info = step_out.get('info', {})
            if done_val and "grade" in info:
                # We reached terminal state
                pass
            
            log_step(step=step, thought=thought, action=action_str, reward=reward_val, done=done_val, error=None)
            rewards.append(reward_val)
            
            messages.append({"role": "assistant", "content": json.dumps(action_data)})
            messages.append({"role": "user", "content": f"Observation: {tool_output}"})
            
            if done_val:
                # The terminal reward is usually the last reward if env is compliant
                if "grade" in info:
                    final_score = info["grade"]["score"]
                    print(f"  --> Terminal Grade Payload Received: Score={final_score}")
                break
                
        except Exception as e:
            error_val = str(e).replace('\n', ' ')
            log_step(step=step, thought="error", action="error", reward=0.0, done=True, error=error_val)
            break
            
    # Grade the episode
    try:
        grade_res = requests.post(f"{ENV_URL}/grade", params={"session_id": session_id})
        grade_out = grade_res.json()
        score = grade_out['score']
        success = score > 0.6
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    except Exception as e:
        print(f"Failed to grade: {e}")
        log_end(success=False, steps=steps_taken, score=0.0, rewards=rewards)

if __name__ == "__main__":
    for lvl in [1, 2, 3]:
        run_task_level(lvl)
