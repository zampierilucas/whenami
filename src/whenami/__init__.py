"""whenami calendar utility package"""

import importlib.metadata
import subprocess
import os

def _get_fallback_version():
    """Get version from git when package is not installed"""
    try:
        # Get current directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to the project root (two levels up from src/whenami)
        project_root = os.path.dirname(os.path.dirname(current_dir))

        # Get the 8-digit SHA
        result = subprocess.run(
            ["git", "rev-parse", "--short=8", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"

try:
    __version__ = importlib.metadata.version("whenami")
except importlib.metadata.PackageNotFoundError:
    # Fallback for development/testing
    __version__ = _get_fallback_version()
