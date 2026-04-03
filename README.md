---
title: SafeGuard Env
emoji: 🏢
colorFrom: blue
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# SafeGuard-Env

## Environment Description & Motivation
An AI Data Compliance Officer Environment validating the "Meta OpenEnv framework" specifications exactly.
This environment addresses a crucial Enterprise pain point: identifying and removing high-value leaked secrets or Protected Personally Identifiable Information (PII) from dynamic corporate streams (emails, server logs, slack chats). 
It goes past static dataset cleaning to interactive tasks handling logic, hallucination detection, and iterative API interactions. It is not a game/toy but directly replicates live Data Scrubbers.

## Tasks and Expected Difficulty
The environment houses a corpus dictating tasks categorized specifically by expected difficulty for RL model progression constraints:
* **Task Level 1 (Easy):** Redacting heavily deterministic, clear regex-pattern footprints (e.g. `192.168.1.1` routing logs or `support@test.org` system endpoints).
* **Task Level 2 (Medium):** Redacting natural context conversational names without strict bounds (e.g. `Hey Jason, check Sarah's data packet.` -> Targets: "Jason", "Sarah").
* **Task Level 3 (Hard):** Redacting extreme-entropy structural secrets embedded loosely over code strings (e.g. AWS Keys or Bearer Tokens scattered through a curl request snippet).

## Observation & Action Space Definitions

### Observation Space
A returned Pydantic construct outlining:
- `document_id`: The ID mapping the isolated data context.
- `text`: The string containing uncleaned system logs/context records.
- `level`: The integer difficulty setting corresponding to [1=Easy, 2=Medium, 3=Hard].

### Action Space (Pydantic `Action`)
The agent enforces redactions by submitting slice actions against the Observation string directly:
- `start_index` (int): Offset marking the structural start of the PII trace.
- `end_index` (int): Exclusive character offset finishing the inclusion range.
- `label` (str): Label context of the traced item (e.g. 'EMAIL', 'API_KEY', 'NAME').

## Graders & Meaningful Reward Construct
* **Graders:** Deterministic evaluators scoring the performance across all secrets. A unified Grader metric (0.0 - 1.0) scores interactions returning a normalized F1 score computed strictly using isolated precision and recall values across correct offsets versus required footprint offsets.
* **Trajectory Meaningful Reward:** Continuous reward flow penalizing destruction metrics over binary states. Rewards isolated step logic (+0.5 matching valid redaction traces), deducts (-0.5 against invalid hallucination redactions on non-PII values) iteratively, and enforces trailing deductions (-1.0 point penalty for missed active secrets).

### Game Theory & Novelty: "Decoy Honeypots"
To specifically measure an LLM's true contextual reasoning rather than its blind pattern matching, the environment explicitly injects **"Decoy Honeypots"** into the data structures (e.g. *"Here is a mock test key: sk-test-000"*). If the agent falls for the trap and attempts to redact the dummy value, the system triggers a **FATAL** violation, slamming the agent with a devastating `-1.0` penalty and collapsing their Precision grading limits natively. This ensures models learn to deeply evaluate semantic context rather than running simple RAG regex passes!

## Usage Instructions
Utilizing OpenEnv compliant endpoints, start the system API locally parsing logic across Docker:
```bash
docker build -t safeguard-env .
docker run -p 7860:7860 safeguard-env
```
Run the inference script which actively tests execution across Task levels 1, 2, and 3 reproducibly.
```bash
export HF_TOKEN="sk-api-key"
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
python inference.py
```
