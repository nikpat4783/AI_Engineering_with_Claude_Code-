import json
from datetime import datetime
from pathlib import Path
from typing import Any


def append_audit_event(event_type: str, payload: dict[str, Any], log_path: Path | None = None) -> None:
    from .config import AUDIT_LOG_PATH
    path = log_path or AUDIT_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        **payload
    }
    with open(path, "a") as f:
        f.write(json.dumps(event) + "\n")


def read_audit_log(log_path: Path | None = None) -> list[dict[str, Any]]:
    from .config import AUDIT_LOG_PATH
    path = log_path or AUDIT_LOG_PATH
    if not path.exists():
        return []
    events = []
    with open(path) as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events
