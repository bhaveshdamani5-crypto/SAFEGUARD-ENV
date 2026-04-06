# SafeGuard Env Demo

This folder contains the Gradio demo application for the SafeGuard Env project.

## Launch locally

```bash
pip install -r demo/requirements.txt
python app.py
```

Then browse to `http://localhost:7860`.

## Demo features

- Upload or paste `.env` content
- Encrypt secrets with AES-256-GCM
- View masked secret previews
- Generate scoped share tokens
- Run basic GitHub leak detection

## Deploy to Hugging Face Spaces

Use `python deploy_to_hf.py` from the repository root after setting `HF_TOKEN`. The demo entrypoint is `app.py` in the repository root, which forwards to the Gradio demo implementation.
