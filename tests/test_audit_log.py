import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triage.audit import append_audit_event, read_audit_log


def test_audit_log_append():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        log_path = Path(f.name)

    try:
        append_audit_event("search", {"query": "test", "hits": 5}, log_path)
        append_audit_event("grounding_check", {"ok": True}, log_path)

        events = read_audit_log(log_path)
        assert len(events) == 2
        assert events[0]["event_type"] == "search"
        assert events[1]["event_type"] == "grounding_check"
        assert "timestamp" in events[0]
        print("✓ test_audit_log_append passed")
    finally:
        log_path.unlink()


def test_audit_log_immutable():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        log_path = Path(f.name)

    try:
        append_audit_event("event1", {"data": "first"}, log_path)
        events_v1 = read_audit_log(log_path)
        first_event = events_v1[0]

        append_audit_event("event2", {"data": "second"}, log_path)
        events_v2 = read_audit_log(log_path)

        assert events_v2[0] == first_event  # First event unchanged
        assert len(events_v2) == 2
        print("✓ test_audit_log_immutable passed")
    finally:
        log_path.unlink()


if __name__ == "__main__":
    test_audit_log_append()
    test_audit_log_immutable()
