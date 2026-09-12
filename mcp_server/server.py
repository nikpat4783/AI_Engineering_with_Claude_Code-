import json
import sys
import uuid
from pathlib import Path
from datetime import datetime
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp.server import Server
from mcp.types import TextContent
from triage.corpus import load_corpus
from triage.allowlist import load_allowlist
from triage.reviewers import load_reviewers
from triage.retriever import build_index, query
from triage.confidence import compute_confidence
from triage.grounding import validate_citations
from triage.schema import Citation, TriageResult
from triage.audit import append_audit_event
from triage.config import RESULTS_DIR


server = Server("triage-corpus")

SEARCH_STORE: dict[str, set[str]] = {}
DOCUMENTS = None
ALLOWLIST = None


def _initialize():
    global DOCUMENTS, ALLOWLIST
    DOCUMENTS = load_corpus(Path.cwd().parent / "corpus" / "docs")
    ALLOWLIST = load_allowlist()


@server.call_tool()
async def search_corpus(query_text: str, top_k: int = 6, min_score: float = 0.15) -> str:
    if DOCUMENTS is None or ALLOWLIST is None:
        _initialize()

    search_id = str(uuid.uuid4())
    index = build_index(list(DOCUMENTS.values()), ALLOWLIST)
    hits = query(index, DOCUMENTS, query_text, top_k=top_k, min_score=min_score)
    hit_ids = {hit.source_id for hit in hits}
    SEARCH_STORE[search_id] = hit_ids

    append_audit_event("search", {
        "search_id": search_id,
        "query": query_text,
        "num_hits": len(hits),
        "excluded_count": index.excluded_count,
        "hit_source_ids": list(hit_ids)
    })

    hits_data = [
        {
            "source_id": hit.source_id,
            "source_type": hit.source_type,
            "title": hit.title,
            "status": hit.status,
            "score": hit.score
        }
        for hit in hits
    ]

    return json.dumps({
        "search_id": search_id,
        "hits": hits_data,
        "excluded_count": index.excluded_count
    })


@server.call_tool()
async def get_document(source_id: str) -> str:
    if DOCUMENTS is None or ALLOWLIST is None:
        _initialize()

    if not ALLOWLIST.is_allowed(source_id):
        append_audit_event("document_access_denied", {
            "source_id": source_id,
            "reason": "not_allowed"
        })
        return json.dumps({"error": f"Document {source_id} is not allowed for retrieval."})

    if source_id not in DOCUMENTS:
        append_audit_event("document_access_denied", {
            "source_id": source_id,
            "reason": "not_found"
        })
        return json.dumps({"error": f"Document {source_id} not found."})

    doc = DOCUMENTS[source_id]
    return json.dumps({
        "source_id": doc.source_id,
        "source_type": doc.source_type,
        "title": doc.title,
        "date": doc.date,
        "org_or_venue": doc.org_or_venue,
        "status": doc.status,
        "body": doc.body
    })


@server.call_tool()
async def validate_citations(search_id: str, cited_source_ids: list[str]) -> str:
    if DOCUMENTS is None or ALLOWLIST is None:
        _initialize()

    if search_id not in SEARCH_STORE:
        return json.dumps({
            "ok": False,
            "invalid_ids": cited_source_ids,
            "reason": f"Search {search_id} not found"
        })

    hit_ids = SEARCH_STORE[search_id]
    invalid_ids = []

    for cited_id in cited_source_ids:
        if not ALLOWLIST.is_allowed(cited_id):
            invalid_ids.append(cited_id)
        elif cited_id not in hit_ids:
            invalid_ids.append(cited_id)

    if invalid_ids:
        append_audit_event("grounding_check", {
            "search_id": search_id,
            "cited_ids": cited_source_ids,
            "ok": False,
            "invalid_ids": invalid_ids
        })
        return json.dumps({"ok": False, "invalid_ids": invalid_ids})

    append_audit_event("grounding_check", {
        "search_id": search_id,
        "cited_ids": cited_source_ids,
        "ok": True,
        "invalid_ids": []
    })

    return json.dumps({"ok": True, "invalid_ids": []})


@server.call_tool()
async def compute_confidence(citations_data: list[dict[str, Any]]) -> str:
    citations = [
        Citation(
            source_id=c["source_id"],
            source_type=c["source_type"],
            title=c["title"],
            status=c["status"],
            relevance_score=c["relevance_score"]
        )
        for c in citations_data
    ]

    cb = compute_confidence(citations)

    append_audit_event("confidence_computed", {
        "num_citations": len(citations),
        "score": cb.score,
        "level": cb.level
    })

    return json.dumps({
        "score": cb.score,
        "level": cb.level,
        "num_supporting_sources": cb.num_supporting_sources,
        "mean_relevance_score": cb.mean_relevance_score,
        "agreement": cb.agreement,
        "stale_penalty_applied": cb.stale_penalty_applied,
        "rationale": cb.rationale
    })


@server.call_tool()
async def submit_result(result_data: dict[str, Any]) -> str:
    result_id = str(uuid.uuid4())
    result_path = RESULTS_DIR / f"{result_id}.json"

    result = TriageResult(
        status=result_data["status"],
        question=result_data["question"],
        answer=result_data.get("answer"),
        confidence=result_data["confidence"],
        citations=result_data.get("citations", []),
        gaps=result_data.get("gaps", []),
        generated_at=datetime.utcnow(),
        review_status="pending"
    )

    with open(result_path, "w") as f:
        f.write(result.model_dump_json(indent=2))

    append_audit_event("result_submitted", {
        "result_id": result_id,
        "status": result.status,
        "question": result.question,
        "num_citations": len(result.citations),
        "confidence_level": result.confidence["level"] if isinstance(result.confidence, dict) else result.confidence.level
    })

    return json.dumps({"result_id": result_id, "path": str(result_path)})


if __name__ == "__main__":
    _initialize()
    server.run(sys.stdin.buffer, sys.stdout.buffer)
