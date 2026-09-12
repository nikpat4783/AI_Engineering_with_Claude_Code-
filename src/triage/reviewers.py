import json
from pathlib import Path
from pydantic import BaseModel


class ReviewerEntry(BaseModel):
    id: str
    name: str


class Reviewers(BaseModel):
    reviewers: dict[str, ReviewerEntry]

    def is_valid_reviewer(self, reviewer_id: str) -> tuple[bool, str | None]:
        if reviewer_id in self.reviewers:
            return True, self.reviewers[reviewer_id].name
        return False, None


def load_reviewers(path: Path | None = None) -> Reviewers:
    from .config import REVIEWERS_PATH
    path = path or REVIEWERS_PATH
    if not path.exists():
        raise FileNotFoundError(f"Reviewers not found at {path}")
    with open(path) as f:
        data = json.load(f)
    reviewers = {
        entry["id"]: ReviewerEntry(**entry)
        for entry in data.get("reviewers", [])
    }
    return Reviewers(reviewers=reviewers)
