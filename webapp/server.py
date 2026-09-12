import sys
import json
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triage.corpus import load_corpus
from triage.allowlist import load_allowlist
from triage.reviewers import load_reviewers
from triage.retriever import build_index, query
from triage.grounding import validate_citations
from triage.confidence import compute_confidence
from triage.schema import Citation, ConfidenceBreakdown, TriageResult
from triage.groq_synthesizer import synthesize, GroqAPIError
from triage.results import persist_result
from triage.audit import append_audit_event, read_audit_log
from triage.cli import review_result
from triage.config import RESULTS_DIR


app = FastAPI(title="Triage API")

# Global state (reuse across requests)
DOCUMENTS = None
ALLOWLIST = None
REVIEWERS = None


def _initialize():
    global DOCUMENTS, ALLOWLIST, REVIEWERS
    DOCUMENTS = load_corpus(Path(__file__).parent.parent / "corpus" / "docs")
    ALLOWLIST = load_allowlist()
    REVIEWERS = load_reviewers()


@app.on_event("startup")
async def startup():
    _initialize()


class AskRequest(BaseModel):
    question: str
    groq_api_key: str


class ReviewRequest(BaseModel):
    result_id: str
    reviewer_id: str
    decision: str
    notes: str = ""


@app.post("/api/ask")
async def ask(req: AskRequest):
    """Run the triage pipeline."""
    _initialize()

    question = req.question.strip()
    if not question:
        return {"error": "Question cannot be empty"}

    try:
        # Step 1: Search
        index = build_index(list(DOCUMENTS.values()), ALLOWLIST)
        hits = query(index, DOCUMENTS, question, top_k=6, min_score=0.15)

        append_audit_event("search", {
            "question": question,
            "num_hits": len(hits),
            "excluded_count": index.excluded_count
        })

        # Zero hits → refused immediately
        if not hits:
            result = TriageResult(
                status="refused",
                question=question,
                answer=None,
                confidence=ConfidenceBreakdown(
                    score=0.0, level="none", num_supporting_sources=0,
                    mean_relevance_score=0.0, agreement=0.0, stale_penalty_applied=False,
                    rationale="No allowlisted evidence retrieved."
                ),
                citations=[],
                gaps=["No allowlisted evidence retrieved for this question."],
                generated_at=datetime.utcnow(),
                review_status="pending"
            )
            result_id, _ = persist_result(result)
            return {"result_id": result_id, "result": result.model_dump()}

        # Step 2-3: Draft and validate (with one retry)
        draft = None
        grounding = None
        for attempt in range(2):
            try:
                corrective = None
                if attempt > 0 and grounding and not grounding.ok:
                    corrective = (
                        f"You cited {grounding.invalid_ids} which were not in the provided evidence. "
                        f"Cite only source_ids from the list you were given."
                    )

                draft = synthesize(question, hits, DOCUMENTS, req.groq_api_key, corrective_note=corrective)

                append_audit_event("llm_synthesis", {
                    "attempt": attempt + 1,
                    "model": "openai/gpt-oss-120b",
                    "num_cited": len(draft.cited_source_ids)
                })

                grounding = validate_citations("", draft.cited_source_ids, hits, ALLOWLIST)

                if grounding.ok:
                    break
            except GroqAPIError as e:
                return {"error": f"API error: {str(e)}"}

        # Still ungrounded → escalated
        if not grounding or not grounding.ok:
            result = TriageResult(
                status="escalated",
                question=question,
                answer=None,
                confidence=ConfidenceBreakdown(
                    score=0.0, level="none", num_supporting_sources=0,
                    mean_relevance_score=0.0, agreement=0.0, stale_penalty_applied=False,
                    rationale="Ungrounded citation(s) after retry."
                ),
                citations=[],
                gaps=[f"Model could not produce a grounded answer. Invalid citation(s): {grounding.invalid_ids if grounding else []}. Escalating for human review."],
                generated_at=datetime.utcnow(),
                review_status="pending"
            )
            result_id, _ = persist_result(result)
            return {"result_id": result_id, "result": result.model_dump()}

        # Step 4: Compute confidence
        cb = compute_confidence(grounding.citations)

        # Step 5: Persist result
        status = "answered" if cb.level in ("high", "medium") else "low_confidence"
        gaps = list(draft.gaps) if draft else []
        if index.excluded_count:
            gaps.append(f"{index.excluded_count} document(s) excluded by allowlist policy.")

        result = TriageResult(
            status=status,
            question=question,
            answer=draft.answer if draft else "",
            confidence=cb,
            citations=grounding.citations,
            gaps=gaps,
            generated_at=datetime.utcnow(),
            review_status="pending"
        )
        result_id, _ = persist_result(result)
        return {"result_id": result_id, "result": result.model_dump(mode="json")}

    except Exception as e:
        return {"error": f"Internal error: {str(e)}"}


@app.get("/api/reviewers")
async def get_reviewers():
    """List available reviewers."""
    _initialize()
    return [{"id": id_, "name": rev.name} for id_, rev in REVIEWERS.reviewers.items()]


@app.get("/api/results")
async def get_results():
    """List all results, newest first."""
    _initialize()
    results = []
    for result_file in sorted(RESULTS_DIR.glob("*.json"), reverse=True):
        if result_file.name.endswith(".review.json"):
            continue
        try:
            with open(result_file) as f:
                data = json.load(f)
            results.append({
                "id": result_file.stem,
                "question": data.get("question"),
                "status": data.get("status"),
                "confidence_level": data.get("confidence", {}).get("level"),
                "review_status": data.get("review_status", "pending"),
                "generated_at": data.get("generated_at"),
                "num_citations": len(data.get("citations", []))
            })
        except Exception:
            pass
    return results


@app.post("/api/review")
async def submit_review(req: ReviewRequest):
    """Submit a review decision."""
    _initialize()
    try:
        review_result(req.result_id, req.reviewer_id, req.decision, req.notes)
        return {"success": True, "message": f"Result reviewed by {req.reviewer_id}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/audit")
async def get_audit():
    """Get last 50 audit entries."""
    _initialize()
    events = read_audit_log()
    return events[-50:] if events else []


# Serve static files
@app.get("/")
async def serve_index():
    """Serve index.html."""
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"error": "index.html not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
