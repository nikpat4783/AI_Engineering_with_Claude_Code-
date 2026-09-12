# Web UI for Triage (Groq-backed)

A browser-based interface to test the triage pipeline using your Groq API key. Reuses the retriever, grounding, and confidence logic; only the answer synthesis step calls Groq.

## Quick start

```bash
cd /home/labuser/Downloads/RAG_AGENTIC_SCIENTIFIC
source .venv/bin/activate
pip install -e ".[web]"
uvicorn webapp.server:app --reload --port 8000
```

Open **http://localhost:8000** in your browser.

## How to use

1. **Enter your Groq API key** (password field) — kept in browser session only, never stored on server
2. **Enter a question** or click an example button
3. **Click "Ask"** — the pipeline runs:
   - Searches the corpus (allowlisted docs only)
   - If zero hits, returns `refused` immediately
   - If hits exist, calls Groq to draft an answer + citations
   - Validates citations (must be in the hit set AND allowlisted)
   - If invalid, retries once with corrective prompt
   - If still invalid, returns `escalated` (no answer)
   - Computes confidence from citation agreement + corroboration
   - Returns structured result with `pending_review` status
4. **Review the result** — select a reviewer, decision, optional notes → **Submit Review**
5. **Check audit log** — expand the "Audit Log" panel to see all operations

## Example questions

Three pre-filled examples match the synthetic corpus:

- **✓ Confident**: "What evidence supports NX-14 for treating idiopathic pulmonary fibrosis, and is it safe?"
  - Expects: `answered`, high/medium confidence, 4 citations (PAPER-001/002, TRIAL-001, REPORT-001)

- **⚠ Low Confidence**: "Are there safety concerns about NX-14 across indications, including liver effects?"
  - Expects: `low_confidence`, stale/conflicting evidence, gaps mention TRIAL-002 + REPORT-002

- **✗ Refused**: "What evidence supports compound ZX-88 for treating pancreatic cancer?"
  - Expects: `refused`, zero citations, no Groq call made

## What's happening under the hood

The backend (`webapp/server.py`):
- Loads the same corpus, allowlist, and reviewers as the Claude Code MCP flow
- Reuses `triage.retriever`, `triage.grounding`, `triage.confidence`
- Calls `triage.groq_synthesizer.synthesize()` which POSTs to `https://api.groq.com/openai/v1/chat/completions`
  with your API key and a JSON Schema strict-format schema
- Validates citations with the same grounding check
- Persists results to `results/<id>.json` and appends to `audit/log.jsonl`
- Reviewer decisions write `results/<id>.review.json` (immutable, one-shot)

The frontend (`webapp/static/index.html`):
- Single HTML file, no build step, inline CSS/JS
- API key stored in `sessionStorage` (cleared when tab closes), never sent to a server (only to Groq directly)
- Structured result rendering: status badge, confidence bar, citations table, gaps list
- Recent results list (newest first) with review status
- Audit log viewer (read-only)

## API endpoints

- `POST /api/ask` — `{question, groq_api_key}` → `{result_id, result: TriageResult}`
- `GET /api/reviewers` — `[{id, name}, ...]`
- `GET /api/results` — List all results (id, question, status, confidence, review_status, num_citations, when)
- `POST /api/review` — `{result_id, reviewer_id, decision, notes}` → `{success, message/error}`
- `GET /api/audit` — Last 50 audit log entries
- `GET /` — Serve `index.html`

## Security notes

- **API key**: Never stored on disk. Passed only as a function argument in `groq_synthesizer.synthesize()`. Never logged to `audit/log.jsonl`. Kept in browser's `sessionStorage` between requests in the same session (convenience, not persistence).
- **Retrieval**: Corpus is allowlist-filtered before any LLM sees it. All evidence goes through the same retriever.
- **Grounding**: Citations are validated server-side (not just accepted as-is from Groq).
- **Results**: Persisted with `pending_review` status by default. A reviewer must approve to finalize.

## Testing

All existing tests still pass:
```bash
pytest tests/ -v
./VERIFY.sh
```

The webapp is orthogonal to the Claude Code skill/MCP flow — they can both run independently or in parallel.

## Troubleshooting

**"Connection refused" when starting**
- Make sure port 8000 is not in use. Change with: `uvicorn webapp.server:app --port 8001`

**"API key validation error"**
- Check that your Groq API key is valid and has the `openai/gpt-oss-120b` model enabled.

**"No evidence retrieved"**
- The question may not match any allowlisted documents closely enough. Try the pre-filled examples first.

**"Model not found"**
- Ensure the Groq model is currently available: `openai/gpt-oss-120b`. Check Groq docs for latest models.

## Next steps

- Deploy to a cloud platform (render.com, railway.app, etc.) for remote access
- Add user authentication + API key vault instead of browser-side entry
- Integrate with Slack or email for async reviews
- Add document upload to expand the corpus dynamically
