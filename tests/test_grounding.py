import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triage.allowlist import Allowlist, SourceEntry
from triage.retriever import RetrievalHit
from triage.grounding import validate_citations


def test_grounding_valid_citations():
    hits = [
        RetrievalHit(source_id="DOC-001", source_type="paper", title="Test1", status="active", raw_score=10.0, score=0.9),
        RetrievalHit(source_id="DOC-002", source_type="paper", title="Test2", status="active", raw_score=8.0, score=0.72)
    ]

    allowlist = Allowlist(
        version=1,
        sources={
            "DOC-001": SourceEntry(source_id="DOC-001", allowed=True, source_type="paper", domain="good.com"),
            "DOC-002": SourceEntry(source_id="DOC-002", allowed=True, source_type="paper", domain="good.com"),
        }
    )

    result = validate_citations("search-001", ["DOC-001", "DOC-002"], hits, allowlist)
    assert result.ok is True
    assert result.invalid_ids == []
    assert len(result.citations) == 2
    print("✓ test_grounding_valid_citations passed")


def test_grounding_disallowed():
    hits = [
        RetrievalHit(source_id="DOC-001", source_type="paper", title="Test1", status="active", raw_score=10.0, score=0.9)
    ]

    allowlist = Allowlist(
        version=1,
        sources={
            "DOC-001": SourceEntry(source_id="DOC-001", allowed=True, source_type="paper", domain="good.com"),
            "DOC-002": SourceEntry(source_id="DOC-002", allowed=False, source_type="paper", domain="bad.com"),
        }
    )

    result = validate_citations("search-001", ["DOC-001", "DOC-002"], hits, allowlist)
    assert result.ok is False
    assert "DOC-002" in result.invalid_ids
    assert result.citations == []
    print("✓ test_grounding_disallowed passed")


def test_grounding_not_in_hits():
    hits = [
        RetrievalHit(source_id="DOC-001", source_type="paper", title="Test1", status="active", raw_score=10.0, score=0.9)
    ]

    allowlist = Allowlist(
        version=1,
        sources={
            "DOC-001": SourceEntry(source_id="DOC-001", allowed=True, source_type="paper", domain="good.com"),
            "DOC-002": SourceEntry(source_id="DOC-002", allowed=True, source_type="paper", domain="good.com"),
        }
    )

    result = validate_citations("search-001", ["DOC-001", "DOC-002"], hits, allowlist)
    assert result.ok is False
    assert "DOC-002" in result.invalid_ids
    assert result.citations == []
    print("✓ test_grounding_not_in_hits passed")


if __name__ == "__main__":
    test_grounding_valid_citations()
    test_grounding_disallowed()
    test_grounding_not_in_hits()
