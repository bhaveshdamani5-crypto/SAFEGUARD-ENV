"""
SafeGuard-Env — OpenEnv-compliant FastAPI Server.

This is the standard OpenEnv server/app.py entry point. It imports and
re-exports the FastAPI application from the project root's main.py so that
`openenv validate` discovers the correct structure while preserving the
full implementation in main.py.
"""
import sys
import os

# Ensure the project root is on the import path so main.py is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: F401 — re-export the FastAPI app
import uvicorn

# Standard OpenEnv convention: module-level `app` object
__all__ = ["app"]

def main() -> None:
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        log_level="info",
    )

if __name__ == "__main__":
    main()
