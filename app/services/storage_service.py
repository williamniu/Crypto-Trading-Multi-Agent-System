from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StorageService:
    """Simple JSON file persistence for traces and workflow artifacts."""

    base_dir: str = "app/audits"

    def write_json(self, relative_path: str, payload: dict[str, Any]) -> Path:
        target = Path(self.base_dir) / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return target
