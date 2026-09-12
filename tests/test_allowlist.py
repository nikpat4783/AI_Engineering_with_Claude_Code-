import sys
import json
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triage.allowlist import load_allowlist


def test_load_allowlist():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        data = {
            "version": 1,
            "sources": [
                {"source_id": "DOC-001", "allowed": True, "source_type": "paper", "domain": "example.com"},
                {"source_id": "DOC-002", "allowed": False, "source_type": "paper", "domain": "bad.com"},
            ]
        }
        json.dump(data, f)
        f.flush()
        path = Path(f.name)

    try:
        allowlist = load_allowlist(path)
        assert allowlist.version == 1
        assert len(allowlist.sources) == 2
        assert allowlist.is_allowed("DOC-001") is True
        assert allowlist.is_allowed("DOC-002") is False
        assert allowlist.is_allowed("UNKNOWN") is False
        print("✓ test_load_allowlist passed")
    finally:
        path.unlink()


if __name__ == "__main__":
    test_load_allowlist()
