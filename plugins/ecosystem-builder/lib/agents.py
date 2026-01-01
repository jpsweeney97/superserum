"""Multi-agent panel for ecosystem gap analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lib.state import Gap


@dataclass
class AgentResult:
    """Result from a single agent's analysis."""

    agent_name: str
    gaps: list[Gap]
    artifacts_scanned: int
    error: str | None = None

    @property
    def success(self) -> bool:
        """True if agent completed without error."""
        return self.error is None
