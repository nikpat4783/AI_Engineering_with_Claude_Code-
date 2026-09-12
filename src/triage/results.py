import uuid
from pathlib import Path
from datetime import datetime
from .schema import TriageResult
from .audit import append_audit_event
from .config import RESULTS_DIR


def persist_result(result: TriageResult) -> tuple[str, Path]:
    """
    Persist a triage result to results/<id>.json and append to audit log.
    Returns (result_id, path).
    """
    result_id = str(uuid.uuid4())
    result_path = RESULTS_DIR / f"{result_id}.json"

    result.generated_at = datetime.utcnow()

    with open(result_path, "w") as f:
        f.write(result.model_dump_json(indent=2))

    append_audit_event("result_submitted", {
        "result_id": result_id,
        "status": result.status,
        "question": result.question,
        "num_citations": len(result.citations),
        "confidence_level": result.confidence.level
    })

    return result_id, result_path
