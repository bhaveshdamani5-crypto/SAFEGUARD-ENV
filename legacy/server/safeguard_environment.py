"""
SafeGuard Environment Server Implementation.

This module wraps the SafeGuardEnv logic into the standard OpenEnv
Environment interface, supporting reset(), step(), state(), and grade().
"""
import sys
import os

# Ensure the parent directory is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env import SafeGuardEnv

# Re-export for server/app.py usage
__all__ = ["SafeGuardEnv"]
