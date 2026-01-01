"""Event logging for ecosystem-builder runs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Event:
    """A logged event."""

    type: str
    data: dict[str, Any]
    timestamp: str


class EventLogger:
    """Appends events to a JSONL log file."""

    def __init__(self, log_file: Path) -> None:
        self.log_file = log_file
        if not self.log_file.exists():
            self.log_file.touch()

    def log(self, event_type: str, data: dict[str, Any]) -> Event:
        """Log an event and return it."""
        event = Event(
            type=event_type,
            data=data,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        line = json.dumps({
            "type": event.type,
            "data": event.data,
            "timestamp": event.timestamp,
        })

        with self.log_file.open("a") as f:
            f.write(line + "\n")

        return event

    def read_all(self) -> list[Event]:
        """Read all events from the log."""
        events = []
        for line in self.log_file.read_text().strip().split("\n"):
            if not line:
                continue
            data = json.loads(line)
            events.append(Event(
                type=data["type"],
                data=data["data"],
                timestamp=data["timestamp"],
            ))
        return events
