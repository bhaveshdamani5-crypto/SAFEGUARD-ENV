import random
from models import Observation, Action, StepResult, StateResponse, GraderResult
from typing import List, Dict, Any

DOCUMENTS = [
    {
        "id": "doc_1",
        "level": 1,
        "text": "Alert: Sysadmin sysadmin@domain.com from IP 192.168.0.50. Whitelisted mock IP is 127.0.0.1.",
        "secrets": [
            {"label": "EMAIL", "text": "sysadmin@domain.com"},
            {"label": "IP", "text": "192.168.0.50"}
        ],
        "honeypots": [{"text": "127.0.0.1"}]
    },
    {
        "id": "doc_2",
        "level": 1,
        "text": "Delete the record for support@test.org. Ignore system-generated example@test.org.",
        "secrets": [
            {"label": "EMAIL", "text": "support@test.org"}
        ],
        "honeypots": [{"text": "example@test.org"}]
    },
    {
        "id": "doc_3",
        "level": 1,
        "text": "Connection blocked from 172.16.254.1. This is not the standard 8.8.8.8 dns server.",
        "secrets": [
            {"label": "IP", "text": "172.16.254.1"}
        ],
        "honeypots": [{"text": "8.8.8.8"}]
    },
    {
        "id": "doc_4",
        "level": 2,
        "text": "Hey Jason, can you tell Sarah to check the budget? (P.S. Remember our persona 'John Doe' for the pitch).",
        "secrets": [
            {"label": "NAME", "text": "Jason"},
            {"label": "NAME", "text": "Sarah"}
        ],
        "honeypots": [{"text": "John Doe"}]
    },
    {
        "id": "doc_5",
        "level": 2,
        "text": "Customer Emily reported a bug. Dev team lead Peterson will review. Do not notify the test account 'Alice'.",
        "secrets": [
            {"label": "NAME", "text": "Emily"},
            {"label": "NAME", "text": "Peterson"}
        ],
        "honeypots": [{"text": "Alice"}]
    },
    {
        "id": "doc_6",
        "level": 2,
        "text": "Meeting notes: David is out sick. We will use the pseudonym 'Charlie' for the client.",
        "secrets": [
            {"label": "NAME", "text": "David"}
        ],
        "honeypots": [{"text": "Charlie"}]
    },
    {
        "id": "doc_7",
        "level": 3,
        "text": "export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE; export DUMMY_KEY=AKIA_MOCK_KEY_12345; echo 'Deploying'",
        "secrets": [
            {"label": "API_KEY", "text": "AKIAIOSFODNN7EXAMPLE"}
        ],
        "honeypots": [{"text": "AKIA_MOCK_KEY_12345"}]
    },
    {
        "id": "doc_8",
        "level": 3,
        "text": "curl -H 'Authorization: Bearer sk-live-12345ABCDEF67890' (fallback to sk-test-0000000000)",
        "secrets": [
            {"label": "AUTH_TOKEN", "text": "sk-live-12345ABCDEF67890"}
        ],
        "honeypots": [{"text": "sk-test-0000000000"}]
    },
    {
        "id": "doc_9",
        "level": 3,
        "text": "const dbParams = { prod_pwd: 'superSecretPassword123!', demo_pwd: 'password' }; connect();",
        "secrets": [
            {"label": "PASSWORD", "text": "superSecretPassword123!"}
        ],
        "honeypots": [{"text": "password"}]
    }
]

def init_documents():
    for doc in DOCUMENTS:
        for secret in doc["secrets"]:
            idx = doc["text"].find(secret["text"])
            if idx != -1:
                secret["start_index"] = idx
                secret["end_index"] = idx + len(secret["text"])
            else:
                raise ValueError(f"Secret {secret['text']} not found in {doc['id']}")

        for hp in doc.get("honeypots", []):
            idx = doc["text"].find(hp["text"])
            if idx != -1:
                hp["start_index"] = idx
                hp["end_index"] = idx + len(hp["text"])
            else:
                raise ValueError(f"Honeypot {hp['text']} not found in {doc['id']}")

init_documents()

class SafeGuardEnv:
    def __init__(self):
        self.doc: Optional[Dict[str, Any]] = None
        self.found_secrets = []
        self.hallucinations = 0
        self.honeypot_violations = 0
        self.current_reward = 0.0
        self.is_done = False
        self.redacted_ranges = []

    def reset(self, level: Optional[int] = None) -> Observation:
        if level is not None:
            valid_docs = [d for d in DOCUMENTS if d["level"] == level]
            if not valid_docs:
                raise ValueError(f"No documents found for level {level}")
            self.doc = random.choice(valid_docs)
        else:
            self.doc = random.choice(DOCUMENTS)

        self.found_secrets = []
        self.hallucinations = 0
        self.honeypot_violations = 0
        self.current_reward = 0.0
        self.is_done = False
        self.redacted_ranges = []
        
        return Observation(
            document_id=self.doc["id"],
            text=self.doc["text"],
            level=self.doc["level"]
        )

    def step(self, action: Action) -> StepResult:
        if self.is_done:
            return StepResult(
                observation=Observation(document_id=self.doc["id"], text=self.doc["text"], level=self.doc["level"]),
                reward=0.0,
                done=True,
                info={"reason": "Episode already done."}
            )

        extracted_text = self.doc["text"][action.start_index:action.end_index]
        matched_secret = None
        matched_honeypot = None
        
        for secret in self.doc["secrets"]:
            if secret["start_index"] == action.start_index and secret["end_index"] == action.end_index and secret["label"] == action.label:
                matched_secret = secret
                break

        for hp in self.doc.get("honeypots", []):
            if hp["start_index"] == action.start_index and hp["end_index"] == action.end_index:
                matched_honeypot = hp
                break

        reward_value = 0.0
        info = ""

        if matched_secret:
            if matched_secret not in self.found_secrets:
                self.found_secrets.append(matched_secret)
                reward_value = 0.5
                info = f"Correct redaction for {action.label}."
                self.redacted_ranges.append((action.start_index, action.end_index))
            else:
                info = "Already redacted."
        elif matched_honeypot:
            self.honeypot_violations += 1
            reward_value = -1.0
            info = f"FATAL: Redacted a decoy/honeypot context ('{extracted_text}'). Contextual violation."
            self.redacted_ranges.append((action.start_index, action.end_index))
        else:
            self.hallucinations += 1
            reward_value = -0.5
            info = f"Hallucinated redaction for {action.label}: '{extracted_text}'"
            self.redacted_ranges.append((action.start_index, action.end_index))

        self.current_reward += reward_value

        return StepResult(
            observation=Observation(document_id=self.doc["id"], text=self.doc["text"], level=self.doc["level"]),
            reward=reward_value,
            done=False,
            info={"reason": info}
        )

    def state(self) -> StateResponse:
        if not self.doc:
            return StateResponse(cleaned_text="", current_reward=0.0)
            
        cleaned = list(self.doc["text"])
        for start_idx, end_idx in self.redacted_ranges:
            cleaned[start_idx:end_idx] = list("*" * (end_idx - start_idx))
            
        return StateResponse(
            cleaned_text="".join(cleaned),
            current_reward=self.current_reward
        )

    def grade(self) -> GraderResult:
        if self.is_done:
            tp = len(self.found_secrets)
            fp = self.hallucinations + self.honeypot_violations
            fn = len(self.doc["secrets"]) - tp
            precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0 if tp > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            return GraderResult(precision=precision, recall=recall, score=f1, reward=self.current_reward)
            
        tp = len(self.found_secrets)
        fp = self.hallucinations + self.honeypot_violations
        fn = len(self.doc["secrets"]) - tp
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0 if tp > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        self.current_reward += fn * -1.0
        self.is_done = True
        
        return GraderResult(
            precision=precision,
            recall=recall,
            score=f1,
            reward=self.current_reward
        )

env_instance = SafeGuardEnv()
