import random
import copy
from typing import List, Dict, Any, Optional
from models import Observation, Action, StepResult, StateResponse, GraderResult
from security.crypto import global_vault
import re
import uuid

SCENARIOS = [
    {
        "id": "scenario_1",
        "level": 1,
        "task_description": "Incident Report: A developer may have committed a live API key into the repository. Investigate the filesystem, locate the live key, and redact it. IMPORTANT: Do not modify mock keys designed for the testing suite.",
        "vfs": {
            "/.env": "STRIPE_API_KEY=sk_live_51Mabcde12345\nDEBUG=True",
            "/app/config.py": "MOCK_AWS_KEY='AKIA_MOCK_HZT45_9999'\ndef load_config(): pass",
            "/src/main.py": "import os\nprint('starting')"
        },
        "true_secrets": [{"path": "/.env", "secret": "sk_live_51Mabcde12345"}],
        "honeypots": [{"path": "/app/config.py", "secret": "AKIA_MOCK_HZT45_9999"}]
    },
    {
        "id": "scenario_2",
        "level": 2,
        "task_description": "Incident Report: PII Leak suspected in log files. Find and redact the user email that leaked. Ignore test accounts used by automation systems.",
        "vfs": {
            "/logs/auth.log": "User logged in. IP: 192.168.1.1\nFailed login: realuser@gmail.com - bad password.",
            "/tests/mocks.json": "{\"test_user\": \"automation@test.local\", \"id\": 1}",
            "/app/handlers.py": "def login(user): log(user)"
        },
        "true_secrets": [{"path": "/logs/auth.log", "secret": "realuser@gmail.com"}],
        "honeypots": [{"path": "/tests/mocks.json", "secret": "automation@test.local"}]
    }
]

def secure_init_database():
    """Encrypts scenarios into the SecureVault to prevent static memory extraction of keys."""
    encrypted_scenarios = []
    for s in SCENARIOS:
        enc_s = copy.deepcopy(s)
        enc_s["vfs_encrypted"] = {}
        for path, content in s["vfs"].items():
            enc_s["vfs_encrypted"][path] = global_vault.encrypt_secret(content)
        
        # We don't encrypt the true_secrets/honeypots in this demo just for grading simplicity,
        # but in a real platform they would be encrypted as well.
        encrypted_scenarios.append(enc_s)
    return encrypted_scenarios

ENCRYPTED_SCENARIOS = secure_init_database()

def generate_procedural_scenario() -> Dict[str, Any]:
    dirs = ["/var/www/site/", "/etc/config/", "/usr/local/bin/", "/root/data/"]
    files = ["settings.json", "env.prod", "backup.sql", "main.py", "auth.log"]
    
    scenario = {
        "id": f"scenario_3_{uuid.uuid4().hex[:6]}",
        "level": 3,
        "task_description": "Incident Report: Infinite Procedural Mode. Find the real leaked token (starts with 'sk_live_') and redact it. Ignore fake tokens (e.g. 'MOCK_TOKEN').",
        "vfs": {},
        "true_secrets": [],
        "honeypots": []
    }
    
    num_files = random.randint(5, 8)
    chosen_paths = set()
    while len(chosen_paths) < num_files:
        chosen_paths.add(random.choice(dirs) + random.choice(files))
        
    chosen_paths = list(chosen_paths)
    true_secret_path = chosen_paths[0]
    honeypot_path = chosen_paths[1]
    
    true_secret = f"sk_live_{uuid.uuid4().hex}"
    honeypot_secret = f"MOCK_TOKEN_{uuid.uuid4().hex}"
    
    for path in chosen_paths:
        if path == true_secret_path:
            scenario["vfs"][path] = f"export API_KEY={true_secret}\n"
            scenario["true_secrets"].append({"path": path, "secret": true_secret})
        elif path == honeypot_path:
            scenario["vfs"][path] = f"// TEST KEY\nvar key = '{honeypot_secret}';"
            scenario["honeypots"].append({"path": path, "secret": honeypot_secret})
        else:
            scenario["vfs"][path] = "Nothing to see here... random data."
            
    scenario["vfs_encrypted"] = {}
    for path, content in scenario["vfs"].items():
        scenario["vfs_encrypted"][path] = global_vault.encrypt_secret(content)
        
    return scenario

class SafeGuardEnv:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.scenario: Optional[Dict[str, Any]] = None
        
        # In-memory working file system (encrypted strings)
        self.working_vfs: Dict[str, str] = {}
        
        self.found_secrets = 0
        self.hallucinations = 0
        self.honeypot_violations = 0
        
        # We record what string was replaced where
        self.redaction_log = []
        
        self.current_reward = 0.0
        self.is_done = False

    def reset(self, level: Optional[int] = None) -> Observation:
        if level == 3:
            self.scenario = generate_procedural_scenario()
        elif level is not None:
            valid = [s for s in ENCRYPTED_SCENARIOS if s["level"] == level]
            if not valid:
                raise ValueError(f"No scenarios for level {level}")
            self.scenario = copy.deepcopy(random.choice(valid))
        else:
            self.scenario = copy.deepcopy(random.choice(ENCRYPTED_SCENARIOS))

        self.working_vfs = copy.deepcopy(self.scenario["vfs_encrypted"])
        self.found_secrets = 0
        self.hallucinations = 0
        self.honeypot_violations = 0
        self.redaction_log = []
        self.current_reward = 0.0
        self.is_done = False
        
        return Observation(
            session_id=self.session_id,
            task_description=self.scenario["task_description"],
            tool_output="Environment reset successfully. You are now in the root directory '/'. Use list_directory to explore.",
            level=self.scenario["level"]
        )

    def step(self, action: Action) -> StepResult:
        if self.is_done:
            return StepResult(
                observation=Observation(session_id=self.session_id, task_description=self.scenario["task_description"], tool_output="Episode already done.", level=self.scenario["level"]),
                reward=0.0,
                done=True,
                info={"reason": "Already done."}
            )

        tool = action.tool_name
        args = action.arguments
        tool_output = ""
        reward_value = 0.0
        info = ""

        try:
            if tool == "list_directory":
                path = args.get("path", "/")
                # Ensure trailing slash for finding children
                if not path.endswith("/"):
                    path += "/"
                if path == "//": 
                    path = "/"

                found_entries = set()
                for vfs_path in self.working_vfs.keys():
                    if vfs_path.startswith(path):
                        remainder = vfs_path[len(path):]
                        if not remainder:
                            continue
                        next_part = remainder.split("/")[0]
                        if "/" in remainder:
                            found_entries.add(next_part + "/") # It's a directory
                        else:
                            found_entries.add(next_part) # It's a file
                
                if found_entries:
                    tool_output = f"Contents of {path}:\n" + "\n".join(sorted(list(found_entries)))
                else:
                    tool_output = f"Directory {path} is empty or does not exist."

            elif tool == "read_file":
                path = args.get("path", "")
                if path in self.working_vfs:
                    decrypted = global_vault.decrypt_secret(self.working_vfs[path])
                    tool_output = f"--- BEGIN {path} ---\n{decrypted}\n--- END {path} ---"
                else:
                    tool_output = f"Error: File {path} not found."

            elif tool == "redact_file":
                path = args.get("path", "")
                target_secret = args.get("secret", "")
                replacement = args.get("replacement", "***")
                
                if path in self.working_vfs:
                    decrypted = global_vault.decrypt_secret(self.working_vfs[path])
                    if target_secret and target_secret in decrypted:
                        new_content = decrypted.replace(target_secret, replacement)
                        self.working_vfs[path] = global_vault.encrypt_secret(new_content)
                        self.redaction_log.append({"path": path, "replaced": target_secret})
                        tool_output = f"Success: Redacted '{target_secret}' with '{replacement}' in {path}."
                        reward_value = 0.5
                    else:
                        tool_output = f"Error: Target text '{target_secret}' not found in {path}."
                        reward_value = -0.1
                else:
                    tool_output = f"Error: File {path} not found."

            elif tool == "search_filesystem":
                query = args.get("query", "")
                if not query:
                    tool_output = "Error: empty query argument."
                    reward_value = -0.1
                else:
                    found_files = []
                    for vfs_path, enc_content in self.working_vfs.items():
                        dec_content = global_vault.decrypt_secret(enc_content)
                        if query in dec_content:
                            found_files.append(vfs_path)
                    
                    if found_files:
                        tool_output = f"Query '{query}' found in:\n" + "\n".join(found_files)
                    else:
                        tool_output = f"No results found for '{query}'."
                    
                    # Compute constraint for search (forces AI to balance cost of brute force search vs intelligent directory traversal)
                    reward_value = -0.05

            elif tool == "submit":
                self.is_done = True
                
                # Auto-Grade the episode for compliant RL Terminal state
                final_grade = self.grade()
                
                # Since grade() already added to self.current_reward, we don't need to add it to reward_value
                # But we do need to return the differential reward for *this specific step*
                # grade() modified self.current_reward, the difference is the terminal reward.
                # Actually, let's just let self.current_reward be accumulated, and we'll pass the breakdown in info.
                
                tool_output = f"Task submitted. Final Score: {final_grade.score:.2f} (Precision: {final_grade.precision:.2f}, Recall: {final_grade.recall:.2f})"
                info = {"reason": "Submission initiated.", "grade": final_grade.dict()}
            
            else:
                tool_output = f"Error: Unknown tool '{tool}'."
                reward_value = -0.1

        except Exception as e:
            tool_output = f"Tool Execution Error: {str(e)}"
            reward_value = -0.5

        self.current_reward += reward_value

        return StepResult(
            observation=Observation(
                session_id=self.session_id, 
                task_description=self.scenario["task_description"], 
                tool_output=tool_output, 
                level=self.scenario["level"]
            ),
            reward=reward_value,
            done=self.is_done,
            info={"reason": info}
        )

    def state(self) -> StateResponse:
        state_dump = {}
        if self.scenario:
            for k, v in self.working_vfs.items():
                state_dump[k] = global_vault.decrypt_secret(v)
                
        return StateResponse(
            cleaned_vfs_state=state_dump,
            current_reward=self.current_reward
        )

    def grade(self) -> GraderResult:
        self.is_done = True
        
        tp = 0
        fp = 0
        
        # Check true secrets
        for req in self.scenario["true_secrets"]:
            found = any((r["path"] == req["path"] and req["secret"] in r["replaced"]) for r in self.redaction_log)
            if found:
                tp += 1
                self.current_reward += 1.0

        # Check honeypots (False Positives)
        for hp in self.scenario["honeypots"]:
            violation = any((r["path"] == hp["path"] and hp["secret"] in r["replaced"]) for r in self.redaction_log)
            if violation:
                fp += 1
                self.current_reward -= 2.0 # Heavy penalty for honeypot violation

        # Any other redaction is a hallucination
        total_redactions = len(self.redaction_log)
        hallucinations = total_redactions - tp - fp
        fp += max(0, hallucinations)
        
        fn = len(self.scenario["true_secrets"]) - tp
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else (1.0 if tp > 0 else 0.0)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return GraderResult(
            precision=precision,
            recall=recall,
            score=f1,
            reward=self.current_reward
        )
