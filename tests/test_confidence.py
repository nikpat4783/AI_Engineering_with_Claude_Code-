import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triage.schema import Citation
from triage.confidence import compute_confidence


def test_confidence_zero_citations():
    cb = compute_confidence([])
    assert cb.score == 0.0
    assert cb.level == "none"
    assert cb.num_supporting_sources == 0
    print("✓ test_confidence_zero_citations passed")


def test_confidence_single_citation():
    citations = [
        Citation(source_id="DOC-001", source_type="paper", title="Test", status="active", relevance_score=0.95)
    ]
    cb = compute_confidence(citations)
    assert cb.num_supporting_sources == 1
    assert cb.score < 0.7  # Single citation capped below "high"
    assert cb.level == "medium" or cb.level == "low"
    print("✓ test_confidence_single_citation passed")


def test_confidence_two_active_high():
    citations = [
        Citation(source_id="DOC-001", source_type="paper", title="Test1", status="active", relevance_score=0.90),
        Citation(source_id="DOC-002", source_type="paper", title="Test2", status="active", relevance_score=0.85)
    ]
    cb = compute_confidence(citations)
    assert cb.num_supporting_sources == 2
    assert cb.level == "high" or cb.level == "medium"
    assert cb.stale_penalty_applied is False
    print("✓ test_confidence_two_active_high passed")


def test_confidence_stale_penalty():
    citations_active = [
        Citation(source_id="DOC-001", source_type="paper", title="Test1", status="active", relevance_score=0.90),
        Citation(source_id="DOC-002", source_type="paper", title="Test2", status="active", relevance_score=0.90)
    ]
    cb_active = compute_confidence(citations_active)

    citations_stale = [
        Citation(source_id="DOC-001", source_type="paper", title="Test1", status="active", relevance_score=0.90),
        Citation(source_id="DOC-002", source_type="paper", title="Test2", status="stale", relevance_score=0.90)
    ]
    cb_stale = compute_confidence(citations_stale)

    assert cb_active.score > cb_stale.score
    assert cb_stale.stale_penalty_applied is True
    print("✓ test_confidence_stale_penalty passed")


if __name__ == "__main__":
    test_confidence_zero_citations()
    test_confidence_single_citation()
    test_confidence_two_active_high()
    test_confidence_stale_penalty()
