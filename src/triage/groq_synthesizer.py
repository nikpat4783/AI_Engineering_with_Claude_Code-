import httpx
import json
from .corpus import Document
from .retriever import RetrievalHit
from .schema import DraftAnswer


class GroqAPIError(Exception):
    pass


def synthesize(question: str, hits: list[RetrievalHit], documents_by_id: dict[str, Document],
               api_key: str, corrective_note: str | None = None,
               model: str = "openai/gpt-oss-120b") -> DraftAnswer:
    """
    Call Groq API to draft an answer based on retrieved documents.
    api_key is never logged or persisted — used only for this request.
    """
    if not hits:
        return DraftAnswer(answer="", cited_source_ids=[], gaps=["No evidence provided."])

    # Build excerpts from hits
    excerpts = []
    for hit in hits:
        doc = documents_by_id.get(hit.source_id)
        if doc:
            excerpts.append(f"[{doc.source_id}] {doc.title}\nStatus: {doc.status}\n{doc.body}")

    excerpts_text = "\n\n".join(excerpts)

    # Build system prompt
    system_prompt = (
        "You are an evidence triage assistant. Answer ONLY using the provided excerpts below. "
        "Every factual claim must cite a source_id from the list (e.g., [PAPER-001]). "
        "If evidence is thin, conflicting, or uncertain, list gaps honestly. "
        "Never invent or cite a source_id not provided.\n\n"
        "Available sources:\n" + excerpts_text
    )

    if corrective_note:
        system_prompt += f"\n\n{corrective_note}"

    # JSON schema for strict response format
    json_schema = {
        "name": "TriageDraftAnswer",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "answer": {"type": "string", "description": "The synthesized answer"},
                "cited_source_ids": {"type": "array", "items": {"type": "string"}, "description": "List of source_ids cited"},
                "gaps": {"type": "array", "items": {"type": "string"}, "description": "List of evidence gaps or caveats"}
            },
            "required": ["answer", "cited_source_ids", "gaps"],
            "additionalProperties": False
        }
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "temperature": 0.3,
        "response_format": {
            "type": "json_schema",
            "json_schema": json_schema
        }
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        with httpx.Client() as client:
            resp = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response.text else str(e)
        raise GroqAPIError(f"Groq API error (status {e.response.status_code}): {error_detail}")
    except Exception as e:
        raise GroqAPIError(f"Groq API request failed: {str(e)}")

    data = resp.json()

    # Extract content from response
    try:
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return DraftAnswer(
            answer=parsed.get("answer", ""),
            cited_source_ids=parsed.get("cited_source_ids", []),
            gaps=parsed.get("gaps", [])
        )
    except (KeyError, json.JSONDecodeError, ValueError) as e:
        raise GroqAPIError(f"Failed to parse Groq response: {str(e)}")
