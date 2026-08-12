"""Write report text and JSON data to disk."""

import json
from pathlib import Path


def save_data_to_file(file_path, data):
    """Write a string or a flat dict to a text file."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        if isinstance(data, dict):
            for key, value in data.items():
                file.write(f"{key}: {value}\n")
        elif isinstance(data, str):
            file.write(data)
        else:
            raise TypeError(f"Cannot write {type(data).__name__} to {file_path}")


def json_save(file_path, data):
    """Write data as indented, UTF-8 JSON."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
