import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRIAGE_ROOT = PROJECT_ROOT

ALLOWLIST_PATH = Path(os.environ.get("TRIAGE_ALLOWLIST_PATH", TRIAGE_ROOT / "allowlist.json"))
REVIEWERS_PATH = Path(os.environ.get("TRIAGE_REVIEWERS_PATH", TRIAGE_ROOT / "reviewers.json"))
CORPUS_DIR = Path(os.environ.get("TRIAGE_CORPUS_DIR", TRIAGE_ROOT / "corpus" / "docs"))
AUDIT_LOG_PATH = Path(os.environ.get("TRIAGE_AUDIT_LOG_PATH", TRIAGE_ROOT / "audit" / "log.jsonl"))
RESULTS_DIR = Path(os.environ.get("TRIAGE_RESULTS_DIR", TRIAGE_ROOT / "results"))

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
