"""Safe subprocess execution with timeout handling."""

import subprocess
from typing import Optional, Tuple


def run_command(
    cmd: list[str],
    cwd: str,
    timeout: int = 30,
    capture_output: bool = True,
) -> Tuple[bool, str, str]:
    """
    Run a command safely with timeout.

    Args:
        cmd: Command and arguments as a list
        cwd: Working directory for the command
        timeout: Timeout in seconds
        capture_output: Whether to capture stdout/stderr

    Returns:
        Tuple of (success: bool, stdout: str, stderr: str)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            timeout=timeout,
            capture_output=capture_output,
            text=True,
        )
        return (
            result.returncode == 0,
            result.stdout or "",
            result.stderr or "",
        )
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return False, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return False, "", f"Error running command: {e}"


def command_exists(command: str, cwd: str) -> bool:
    """
    Check if a command is available.

    Args:
        command: Command name (e.g., 'ruff', 'eslint')
        cwd: Working directory

    Returns:
        True if command exists, False otherwise
    """
    import shutil
    import os

    # First check in PATH
    if shutil.which(command):
        return True

    # For Node.js tools, check local node_modules/.bin
    node_modules_bin = os.path.join(cwd, "node_modules", ".bin", command)
    if os.path.isfile(node_modules_bin) and os.access(node_modules_bin, os.X_OK):
        return True

    return False
