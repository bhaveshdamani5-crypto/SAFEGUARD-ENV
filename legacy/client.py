"""
SafeGuard-Env Client — OpenEnv-compatible synchronous/async HTTP client.

This client connects to a running SafeGuard-Env server and provides
Gymnasium-style reset(), step(), state(), and grade() methods.
"""

import requests
from typing import Optional, Dict, Any


class SafeGuardClient:
    """
    Synchronous HTTP client for the SafeGuard-Env OpenEnv environment.

    Usage:
        client = SafeGuardClient(base_url="https://your-space.hf.space")
        obs = client.reset(level=1)
        result = client.step(session_id=obs["session_id"], tool_name="list_directory", arguments={"path": "/"})
        grade = client.grade(session_id=obs["session_id"])
    """

    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()

    def reset(self, level: Optional[int] = None) -> Dict[str, Any]:
        """Reset the environment with an optional difficulty level (1-3)."""
        params = {}
        if level is not None:
            params["level"] = level
        resp = self._session.post(f"{self.base_url}/reset", params=params)
        resp.raise_for_status()
        return resp.json()

    def step(
        self,
        session_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute an agent action and return the StepResult."""
        payload = {
            "session_id": session_id,
            "tool_name": tool_name,
            "arguments": arguments,
        }
        resp = self._session.post(f"{self.base_url}/step", json=payload)
        resp.raise_for_status()
        return resp.json()

    def state(self, session_id: str = "default") -> Dict[str, Any]:
        """Retrieve the current VFS state and reward."""
        resp = self._session.get(
            f"{self.base_url}/state", params={"session_id": session_id}
        )
        resp.raise_for_status()
        return resp.json()

    def grade(self, session_id: str = "default") -> Dict[str, Any]:
        """Compute precision, recall, F1 score, and reward."""
        resp = self._session.post(
            f"{self.base_url}/grade", params={"session_id": session_id}
        )
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
