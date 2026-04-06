# Features

SafeGuard Env is designed to be a production-ready secret management demo with the following capabilities:

- AES-256-GCM encryption for every uploaded secret
- `.env` parsing with immediate transformation into encrypted storage
- Secret versioning for auditability and drift tracking
- Role-based access control with `admin`, `editor`, and `viewer` roles
- Token-based sharing for scoped secret retrieval
- GitHub leak detection logic for `.env` and token patterns
- Risk scoring on secrets as `low`, `medium`, or `high`
- Gradio-powered demo for fast deployment on Hugging Face Spaces
- Modular folder structure for frontend, backend, encryption, docs, and demo
