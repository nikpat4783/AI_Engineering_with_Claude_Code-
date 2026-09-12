import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triage.corpus import load_corpus
from triage.allowlist import load_allowlist


def test_corpus_allowlist_consistency():
    corpus = load_corpus(Path(__file__).parent.parent / "corpus" / "docs")
    allowlist = load_allowlist(Path(__file__).parent.parent / "allowlist.json")

    corpus_ids = set(corpus.keys())
    allowlist_ids = set(allowlist.sources.keys())

    assert corpus_ids == allowlist_ids, f"Mismatch: corpus={corpus_ids}, allowlist={allowlist_ids}"
    print(f"  ✓ {len(corpus_ids)} documents in corpus, all in allowlist")

    for doc_id, doc in corpus.items():
        if doc.status == "retracted":
            assert not allowlist.is_allowed(doc_id), f"{doc_id} is retracted but allowed"
    print("  ✓ retracted documents are never allowed")

    print("✓ test_corpus_allowlist_consistency passed")


if __name__ == "__main__":
    test_corpus_allowlist_consistency()
