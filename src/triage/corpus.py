import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel


class Document(BaseModel):
    source_id: str
    source_type: Literal["paper", "patent", "trial_registry", "internal_report"]
    title: str
    date: str
    org_or_venue: str
    status: Literal["active", "stale", "retracted"]
    body: str


def load_corpus(corpus_dir: Path) -> dict[str, Document]:
    docs = {}
    if not corpus_dir.exists():
        return docs
    for doc_file in sorted(corpus_dir.glob("*.json")):
        try:
            with open(doc_file) as f:
                data = json.load(f)
                doc = Document(**data)
                docs[doc.source_id] = doc
        except Exception as e:
            raise ValueError(f"Failed to load {doc_file}: {e}")
    return docs
