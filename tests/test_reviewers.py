import sys
import json
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triage.reviewers import load_reviewers


def test_load_reviewers():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        data = {
            "reviewers": [
                {"id": "jsmith", "name": "Jane Smith"},
                {"id": "rjones", "name": "Robert Jones"},
            ]
        }
        json.dump(data, f)
        f.flush()
        path = Path(f.name)

    try:
        reviewers = load_reviewers(path)
        valid, name = reviewers.is_valid_reviewer("jsmith")
        assert valid is True
        assert name == "Jane Smith"

        valid, name = reviewers.is_valid_reviewer("unknown")
        assert valid is False
        assert name is None

        print("✓ test_load_reviewers passed")
    finally:
        path.unlink()


if __name__ == "__main__":
    test_load_reviewers()
