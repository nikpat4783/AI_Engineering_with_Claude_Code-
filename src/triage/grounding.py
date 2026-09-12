from .allowlist import Allowlist
from .retriever import RetrievalHit
from .schema import Citation, GroundingResult


def validate_citations(search_id: str, cited_source_ids: list[str], hits: list[RetrievalHit],
                       allowlist: Allowlist, searches: dict[str, set[str]] | None = None) -> GroundingResult:
    if searches is None:
        searches = {}

    hit_ids = {hit.source_id for hit in hits}
    invalid_ids = []

    for cited_id in cited_source_ids:
        if not allowlist.is_allowed(cited_id):
            invalid_ids.append(cited_id)
        elif cited_id not in hit_ids:
            invalid_ids.append(cited_id)

    if invalid_ids:
        return GroundingResult(ok=False, invalid_ids=invalid_ids, citations=[])

    citations = [
        Citation(
            source_id=hit.source_id,
            source_type=hit.source_type,
            title=hit.title,
            status=hit.status,
            relevance_score=hit.score
        )
        for hit in hits
        if hit.source_id in cited_source_ids
    ]

    return GroundingResult(ok=True, invalid_ids=[], citations=citations)
