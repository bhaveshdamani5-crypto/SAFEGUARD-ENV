# Contributing to SafeGuard Env

Thank you for helping improve SafeGuard Env.

## How to contribute

1. Fork the repository.
2. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/my-improvement
   ```

````
3. Install dependencies in a virtual environment:
   ```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
````

4. Make your changes and test them.
5. Add and commit your changes with a clear message:
   ```bash
   git add .
   git commit -m "feat: describe what changed"
   ```

```
6. Push your branch and open a pull request.

## Notes

- Keep the project structure clean: `backend/`, `encryption/`, `demo/`, `frontend/`, `docs/`.
- Update docs when you add features.
- Use the demo app to verify both `.env` encryption and masked preview flows.
- Do not commit secrets or API keys.

## Reporting bugs

Please open an issue describing:
- What you tried to do
- What happened
- What you expected to happen
- Steps to reproduce
```
