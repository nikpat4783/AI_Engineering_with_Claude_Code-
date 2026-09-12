import json
import re
from pathlib import Path
from typing import Literal
from pydantic import BaseModel


class SourceEntry(BaseModel):
    source_id: str
    allowed: bool
    source_type: Literal["paper", "patent", "trial_registry", "internal_report"]
    domain: str


class Allowlist(BaseModel):
    version: int
    sources: dict[str, SourceEntry]

    def is_allowed(self, source_id: str) -> bool:
        return self.sources.get(source_id, SourceEntry(
            source_id=source_id, allowed=False, source_type="paper", domain=""
        )).allowed


NETWORK_DENY_PATTERNS = [
    re.compile(r'\bcurl\b'),
    re.compile(r'\bwget\b'),
    re.compile(r'\bnc\b'),
    re.compile(r'\bncat\b'),
    re.compile(r'\bnetcat\b'),
    re.compile(r'\btelnet\b'),
    re.compile(r'https?://'),
    re.compile(r'\burllib\.(request|error)\b'),
    re.compile(r'\brequests\.(get|post|put|delete|head)\b'),
    re.compile(r'\bhttpx\b'),
    re.compile(r'\bsocket\.(connect|create_connection)\b'),
    re.compile(r'\bscp\b'),
    re.compile(r'\bsftp\b'),
]


def load_allowlist(path: Path | None = None) -> Allowlist:
    from .config import ALLOWLIST_PATH
    path = path or ALLOWLIST_PATH
    if not path.exists():
        raise FileNotFoundError(f"Allowlist not found at {path}")
    with open(path) as f:
        data = json.load(f)
    sources = {
        entry["source_id"]: SourceEntry(**entry)
        for entry in data.get("sources", [])
    }
    return Allowlist(version=data.get("version", 1), sources=sources)
