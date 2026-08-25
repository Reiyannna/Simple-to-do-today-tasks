"""Load and save tasks to a JSON file next to this script."""
from __future__ import annotations

import json
import os
from typing import List

from task import Task

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


def load_tasks(path: str = DEFAULT_PATH) -> List[Task]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    return [Task.from_dict(d) for d in raw]


def save_tasks(tasks: List[Task], path: str = DEFAULT_PATH) -> None:
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)
    os.replace(tmp_path, path)
