from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable


class ToolValidationError(ValueError):
    """Raised when a tool payload does not match required fields."""


@dataclass
class BaseTool(ABC):
    """Base contract for all tools used by agents."""

    name: str
    description: str
    required_fields: list[str] = field(default_factory=list)

    def validate(self, payload: dict[str, Any]) -> None:
        missing = [field for field in self.required_fields if field not in payload]
        if missing:
            missing_fields = ", ".join(missing)
            raise ToolValidationError(
                f"Tool '{self.name}' missing required fields: {missing_fields}"
            )

    @abstractmethod
    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute tool logic and return a serializable dict."""

    def __call__(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.validate(payload)
        return self.run(payload)


@dataclass
class FunctionTool(BaseTool):
    """Simple tool wrapper for function-based MVP tool implementations."""

    handler: Callable[[dict[str, Any]], dict[str, Any]] = lambda _: {}

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.handler(payload)
