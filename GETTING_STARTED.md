# Getting Started: Two Ways to Test the Triage System

You now have a complete R&D evidence triage system with **two independent interfaces**:

## Option 1: Claude Code (Interactive Agent)

Best for: Exploring the system with a live Claude agent, testing the full pipeline.

```bash
cd /home/labuser/Downloads/RAG_AGENTIC_SCIENTIFIC
source .venv/bin/activate
claude
```

In Claude Code:
```
/triage "What evidence supports NX-14 for treating idiopathic pulmonary fibrosis, and is it safe?"
```

Then review:
```bash
python -m triage review <result_id> --reviewer jsmith --decision approve
```

**Pros**: Full agent loop, real-time interaction, MCP server integration  
**Cons**: Requires Claude Code session, depends on Anthropic API (if not using Groq via MCP)

---

## Option 2: Web UI (Groq-backed)

Best for: Quick browser-based testing, bringing your own Groq API key, no CLI needed.

```bash
cd /home/labuser/Downloads/RAG_AGENTIC_SCIENTIFIC
source .venv/bin/activate
uvicorn webapp.server:app --reload --port 8000
```

Open **http://localhost:8000**

1. Paste your Groq API key (gsk_...)
2. Enter a question (or click an example)
3. Click "Ask"
4. Review the structured result
5. Approve/reject via the review panel

**Pros**: Browser-based, no Claude Code needed, user brings their own Groq key  
**Cons**: Web-only, no MCP

---

## What's identical between them

Both flows:
- ✓ Search the same allowlisted corpus (BM25 retrieval)
- ✓ Validate citations against the hit set (grounding check)
- ✓ Compute confidence from citation agreement + corroboration
- ✓ Return structured output: {status, answer, confidence, citations, gaps}
- ✓ Require human reviewer approval (`pending_review` → approved/rejected)
- ✓ Write immutable audit log
- ✓ Enforce the four commitments: retrieval from approved sources, grounded claims, structured output, graceful failures

The only difference: **who drafts the answer**
- Claude Code flow: Claude (Anthropic API)
- Web UI flow: Groq (openai/gpt-oss-120b model)

---

## The three demo scenarios

### 1. Confident, well-grounded answer
**Question**: "What evidence supports NX-14 for treating idiopathic pulmonary fibrosis, and is it safe?"

**Expected**:
- Status: ✓ `answered`
- Confidence: `high` or `medium`
- Citations: PAPER-001, PAPER-002, TRIAL-001, REPORT-001 (all active, high relevance)
- Gaps: (minimal or none)

### 2. Low-confidence answer (stale/conflicting evidence)
**Question**: "Are there safety concerns about NX-14 across indications, including liver effects?"

**Expected**:
- Status: ⚠ `low_confidence`
- Confidence: `low` (stale penalty applied)
- Citations: TRIAL-002 (stale, terminated), REPORT-002 (stale, superseded)
- Gaps: "Stale evidence from 2019-2020", "TRIAL-002 was terminated for safety signal in different indication", etc.

### 3. Refused (insufficient evidence)
**Question**: "What evidence supports compound ZX-88 for treating pancreatic cancer?"

**Expected**:
- Status: ✗ `refused`
- Answer: null
- Confidence: `none` (score 0.0)
- Citations: [] (empty)
- Gaps: "No allowlisted evidence retrieved for this question."
- LLM never called (zero hits above threshold)

---

## Key files

| File | Purpose |
|---|---|
| `.claude/skills/triage/SKILL.md` | Agent loop spec (trigger, 6 steps, stop conditions, handoff) |
| `webapp/server.py` | FastAPI backend (orchestrates pipeline + Groq synthesis) |
| `webapp/static/index.html` | Single-file HTML/CSS/JS UI, no build step |
| `src/triage/groq_synthesizer.py` | Calls Groq API with JSON Schema strict mode |
| `src/triage/retriever.py` | BM25 index (hand-rolled, no sklearn) |
| `src/triage/confidence.py` | Confidence formula (pure function, fully testable) |
| `src/triage/grounding.py` | Citation validation (allowlist + presence-in-hits) |
| `corpus/docs/*.json` | 11 synthetic documents (papers, patents, trials, reports) |
| `allowlist.json` | Which source_ids are approved |
| `reviewers.json` | Valid reviewer ids |
| `audit/log.jsonl` | Append-only audit trail |
| `results/*.json` | Pipeline outputs (pending review until approved) |

---

## Testing

All tests pass without Groq/Anthropic API keys:

```bash
source .venv/bin/activate
pytest tests/ -v              # 8 unit test modules
./VERIFY.sh                    # Full verification (tests + corpus consistency + hook)
```

---

## What to test first

1. **Unit tests** (no API key needed):
   ```bash
   ./VERIFY.sh
   ```
   Confirms retriever, confidence, grounding, corpus consistency, hook contract all work.

2. **Web UI** (requires Groq API key):
   ```bash
   uvicorn webapp.server:app --port 8000
   # Open http://localhost:8000
   # Paste your Groq key, click "Confident" example → expect well-grounded answer
   ```

3. **Claude Code** (requires Claude Code + Anthropic API key):
   ```bash
   claude
   # In Claude Code: /triage "What evidence supports NX-14 for treating idiopathic pulmonary fibrosis, and is it safe?"
   ```

---

## Next: Extend or deploy

- **Add more documents**: Drop JSON files in `corpus/docs/`, add entries to `allowlist.json`
- **Change reviewers**: Edit `reviewers.json`
- **Adjust confidence formula**: Edit `src/triage/confidence.py` (pure function)
- **Tune retriever**: Edit `src/triage/retriever.py` (BM25 parameters, min_score threshold)
- **Deploy web UI**: See WEBAPP_README.md for cloud deployment options

---

## Support

- Plan: `.claude/plans/r-d-teams-draw-on-calm-emerson.md`
- README: `README.md` (original high-level design)
- Webapp guide: `WEBAPP_README.md` (web UI specifics)
- Architecture: `.claude/skills/triage/SKILL.md` (agent loop spec)
