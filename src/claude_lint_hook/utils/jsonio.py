"""JSON parsing and writing utilities."""

import json
from typing import Any, Dict


def parse_json(text: str) -> Dict[str, Any]:
    """
    Parse JSON text into a dictionary.

    Args:
        text: JSON string

    Returns:
        Parsed dictionary

    Raises:
        ValueError: If JSON is invalid
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def write_json(path: str, data: Dict[str, Any], indent: int = 2) -> None:
    """
    Write dictionary to a JSON file.

    Args:
        path: File path to write to
        data: Dictionary to write
        indent: JSON indentation level
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=indent)


def read_json(path: str) -> Dict[str, Any]:
    """
    Read JSON file into a dictionary.

    Args:
        path: File path to read from

    Returns:
        Parsed dictionary, or empty dict if file doesn't exist
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
