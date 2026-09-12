import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triage.corpus import Document
from triage.allowlist import Allowlist, SourceEntry
from triage.retriever import build_index, query


def test_retriever_excludes_disallowed():
    docs = [
        Document(
            source_id="ALLOWED-001",
            source_type="paper",
            title="Test paper on NX-14",
            date="2024-01-01",
            org_or_venue="Journal",
            status="active",
            body="NX-14 is a ROCK2 inhibitor for IPF"
        ),
        Document(
            source_id="DISALLOWED-001",
            source_type="paper",
            title="Disallowed paper on NX-14",
            date="2024-01-01",
            org_or_venue="Bad Journal",
            status="active",
            body="NX-14 cures everything"
        )
    ]

    allowlist = Allowlist(
        version=1,
        sources={
            "ALLOWED-001": SourceEntry(source_id="ALLOWED-001", allowed=True, source_type="paper", domain="good.com"),
            "DISALLOWED-001": SourceEntry(source_id="DISALLOWED-001", allowed=False, source_type="paper", domain="bad.com"),
        }
    )

    index = build_index(docs, allowlist)
    assert len(index.doc_ids) == 1
    assert index.excluded_count == 1
    assert index.excluded_ids == ["DISALLOWED-001"]

    docs_by_id = {doc.source_id: doc for doc in docs}
    hits = query(index, docs_by_id, "NX-14", top_k=10)
    hit_ids = [h.source_id for h in hits]
    assert "DISALLOWED-001" not in hit_ids
    assert "ALLOWED-001" in hit_ids

    print("✓ test_retriever_excludes_disallowed passed")


def test_retriever_threshold():
    docs = [
        Document(
            source_id="RELEVANT",
            source_type="paper",
            title="NX-14 efficacy in IPF",
            date="2024-01-01",
            org_or_venue="Journal",
            status="active",
            body="NX-14 is effective for idiopathic pulmonary fibrosis"
        ),
        Document(
            source_id="IRRELEVANT",
            source_type="paper",
            title="TX-9 in pancreatic cancer",
            date="2024-01-01",
            org_or_venue="Journal",
            status="active",
            body="TX-9 targets mutant KRAS in pancreatic cancer"
        )
    ]

    allowlist = Allowlist(
        version=1,
        sources={
            "RELEVANT": SourceEntry(source_id="RELEVANT", allowed=True, source_type="paper", domain="good.com"),
            "IRRELEVANT": SourceEntry(source_id="IRRELEVANT", allowed=True, source_type="paper", domain="good.com"),
        }
    )

    index = build_index(docs, allowlist)
    docs_by_id = {doc.source_id: doc for doc in docs}

    # Query for ZX-88, a compound not in corpus
    hits = query(index, docs_by_id, "ZX-88 pancreatic cancer", top_k=10, min_score=0.15)
    # IRRELEVANT might match on "pancreatic cancer" but score should be low
    # RELEVANT should not match
    hit_ids = [h.source_id for h in hits]
    assert "RELEVANT" not in hit_ids
    print(f"  Query 'ZX-88 pancreatic cancer' returned hits: {hit_ids}")
    print("✓ test_retriever_threshold passed")


if __name__ == "__main__":
    test_retriever_excludes_disallowed()
    test_retriever_threshold()
