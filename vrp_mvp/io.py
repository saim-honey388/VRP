from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Instance, Solution


def load_instance(path: str) -> Instance:
    data = json.loads(Path(path).read_text())
    return Instance(**data)


def save_solution(solution: Solution, path: str) -> None:
    out = json.dumps(solution.model_dump(), indent=2)
    Path(path).write_text(out)


