<div align="center">
    <img src="https://img.shields.io/badge/Meta-OpenInnovation-0668E1?style=for-the-badge&logo=meta&logoColor=white"/>
    <img src="https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white"/>
    <img src="https://img.shields.io/badge/Meta_Llama_3-046A38?style=for-the-badge&logo=meta&logoColor=white"/>
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi"/>
    <h1>🌍 SafeGuard-OpenEnv</h1>
    <h3>AI-Powered Real-time Environmental Anomaly & Risk Detection System</h3>
    <p><b>Built specifically for the Meta Open Innovation / OpenEnv Hackathon</b></p>
</div>

<p align="center">
    <em>Deep Learning architecture designed to prevent environmental disasters before they happen, leveraging <b>PyTorch</b> and <b>Meta Llama 3</b> APIs.</em>
</p>

---

## 🚨 The OpenEnv Problem

Every year, undetected industrial leaks, spontaneous factory fires, and slow-building pollution events result in lost lives, billion-dollar damages, and devastating ecological consequences. 

**Traditional sensor networks are reactive.** They use hardcoded thresholds that trigger alarms *after* critical thresholds are breached. They cannot recognize complex, multi-variate warning signs—such as a slight drop in humidity paired with an unusual spike in CO2—before an event actually happens.

## 💡 The SafeGuard-OpenEnv Solution

**SafeGuard-OpenEnv** transforms reactive sensor monitoring into **proactive anomaly prediction**.

By leveraging state-of-the-art **Deep Learning (PyTorch)** and **Meta Llama 3** for incident reporting, the system continuously models the "normal" operational baseline of an environment across multiple variables (Temperature, Humidity, CO2, PM2.5). When a sub-threshold multivariate deviation occurs, it accurately isolates the anomaly, categorizes the risk, and deploys high-priority Llama-3 enhanced alerts via a comprehensive dashboard.

---

## 🧠 Gymnasium Reinforcement Learning (OpenEnv Core)

In strict adherence to the **Meta PyTorch OpenEnv Hackathon x Scaler** requirements, the core AI intelligence is built around a custom **Reinforcement Learning Gymnasium Environment** (`env/safeguard_env.py`).

1. **Custom OpenEnv Framework:** We simulated a realistic industrial hazard scenario inside a standard Gymnasium API container.
2. **Observation Space:** The RL Agent constantly perceives 4 continuous telemetry streams `[Temp, Hum, CO2, PM2.5]`.
3. **Action Space (Mitigation):** The Agent controls facility hardware to prevent disasters:
   - `0`: Continue Operations (No energy cost)
   - `1`: Trigger Ventilation (Reduces CO2/PM2.5, incurs energy penalty)
   - `2`: Trigger Cooling (Reduces Heat, incurs energy penalty)
   - `3`: Emergency Shutdown (Forces baseline safety, massive production penalty)
4. **Proximal Policy Optimization (PPO):** We trained the agent using `stable-baselines3` (PyTorch) to learn the precise balance between maintaining environmental safety and over-using expensive mitigation systems.
5. **Meta Llama 3 Risk Reports:** The agent's selected actions are contextualized via Meta Llama 3 prompts into actionable telemetry reports for human operators via the UI.

---

## 🏗 System Architecture (RL OpenEnv Spec)

The project is built as a complete real-world Hackathon execution.

```mermaid
graph TD
    S[(Sensor Telemetry Stream\nTemp, Hum, CO2, PM2.5)] -->|Observation| A[FastAPI Ingestion Layer]
    A -->|Observation State| B[Trained Gym RL Agent]
    B -->|PPO Inference| B
    B -->|Mitigation Action (0,1,2,3)| D[RL Control Logic]
    D -->|Context| L[Meta Llama 3 Auto-Report API]
    L -->|JSON Stream| E[Real-time Client Dashboard]
    D -->|Sensors Only| E
    
    style S fill:#1f2937,stroke:#94a3b8,color:#f0f4f8
    style A fill:#0ea5e9,stroke:#0284c7,color:#f0f4f8
    style B fill:#ee4c2c,stroke:#b91c1c,color:#f0f4f8
    style L fill:#046A38,stroke:#024A26,color:#f0f4f8
    style E fill:#10b981,stroke:#047857,color:#f0f4f8
```

- **Frontend:** Premium responsive Glassmorphism dashboard leveraging Vanilla JS and Chart.js for real-time risk streaming.
- **Backend:** High-performance asynchronous FastAPI server handling data routing.
- **ML Layer:** PyTorch training harness (`ml/train.py`), synthetic dataset generator (`ml/dataset.py`), and TorchScript inference.

---

## 📊 Innovation Boosts

1. **Edge-AI Compatibility:** Exported TorchScript graph execution allows deployment directly on ARM/Edge IoT devices without standard Python dependencies.
2. **Multi-variate Sensoring:** Analyzes up to 4 real-time data streams concurrently compared to simple single-variable triggers.
3. **Zero-shot Anomaly Detection:** Requires only "normal" data for training, solving the primary challenge of gathering data for catastrophic factory/forest events that rarely happen.

---

## 🌍 Real-World Impact (OpenEnv)

- **Industrial Safety:** Protects workers by identifying volatile chemical buildup or combustion precursors.
- **Urban Sustainability:** Enables smart cities to instantly detect unauthorized industrial emissions or smog pockets.
- **Ecological Preservation:** Monitors forest borders for immediate wildfire detection by recognizing pre-ignition atmospheric anomalies.

---

## 🚀 Deployment Guide

### Local Deployment (Development)

Run the full product stack locally with Python's fast ASGI server.

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train the PyTorch model (Generates TorchScript .pt)
python -m ml.train

# 4. Start the Application Stack
uvicorn app:app --host 0.0.0.0 --port 7860
```
Then visit: `http://localhost:7860`

### 📦 Docker / Cloud Native

```bash
# Build the production image
docker build -t safeguard-env .

# Run the containerized service
docker run -p 7860:7860 safeguard-env
```

### Hugging Face Spaces Deployment

The repository is built organically for Hugging Face Spaces. Simply create a Space configured to `Docker` or `Gradio/FastAPI` and push the repository!

---

## 🔮 Future Scope

- **Federated Learning:** Train edge nodes locally and aggregate their weights in the cloud, allowing different factories to learn from each other's disaster data privately.
- **Satellite Data Fusion:** Incorporate open computer vision API models (Sentinel-2) to cross-verify terrestrial sensor anomalies with aerial visual data.
- **Automated Mitigation:** Connect with smart factory systems to automatically trigger ventilation or lock down affected pipeline sectors upon critical risk.
