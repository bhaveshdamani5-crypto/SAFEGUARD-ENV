# Security Design

SafeGuard Env is built to demonstrate strong secrets hygiene and a zero-trust approach.

## Encryption Layer

- Uses AES-256-GCM for authenticated encryption.
- Keys can be supplied through `SAFEGUARD_ENV_KEY` as a base64-encoded 32-byte key.
- Secrets are never stored in plain text inside the app; only encrypted blobs and masked previews are exposed.

## Zero Trust Model

- No implicit trust is assumed for uploaded `.env` content.
- Sensitive payloads are encrypted immediately upon ingestion.
- Role-based headers and share tokens are required for any reveal operation.

## Leak Detection

- Basic GitHub leak detection scans for common patterns such as `GITHUB_TOKEN`, `GH_TOKEN`, `API_KEY`, and `.env` references.
- Risk scoring flags suspicious secrets as `low`, `medium`, or `high`.
- This is a demo-ready implementation suitable for additional expansion with real SCM scanning.
