# Deployment & Usage Guide

## What was built

A Claude Code–native agentic system for R&D evidence triage. The system enforces four commitments through a combination of MCP server, Claude Code hook, and skill definition:

1. **Retrieve only from approved sources** (MCP server + PreToolUse hook)
2. **Ground every claim** (grounding check before output)
3. **Return structured output** (answer, confidence, citations, gaps)
4. **Fail gracefully** (refuse or escalate, human reviewer gate)

## All tests pass ✓

Run `./VERIFY.sh` from the project root to confirm:
- ✓ 8 unit test modules (no API key needed)
- ✓ 11 synthetic corpus documents in corpus/docs/
- ✓ Hook contract (PreToolUse hook subprocess tests)
- ✓ Corpus/allowlist consistency
- ✓ Retriever excludes disallowed docs by default
- ✓ Confidence computed from citation agreement + corroboration
- ✓ Grounding validates both allowlist + presence-in-hits

## To run the live agentic loop

```bash
cd /home/labuser/Downloads/RAG_AGENTIC_SCIENTIFIC
source .venv/bin/activate
claude
```

In Claude Code:
```
/triage "What evidence supports NX-14 for treating idiopathic pulmonary fibrosis, and is it safe?"
```

Expected: **pending_review** result citing PAPER-001, PAPER-002, TRIAL-001, REPORT-001, with high/medium confidence.

## The four demo questions

### 1. Confident, well-grounded answer
```
/triage "What evidence supports NX-14 for treating idiopathic pulmonary fibrosis, and is it safe?"
```

**Expected outcome:**
- Status: `answered`
- Confidence: `high` or `medium` (multiple active sources, high agreement)
- Citations: PAPER-001, PAPER-002, TRIAL-001, REPORT-001
- Gaps: (none or only marginal)

### 2. Low-confidence answer (stale/conflicting evidence)
```
/triage "Are there safety concerns about NX-14 across indications, including liver effects?"
```

**Expected outcome:**
- Status: `low_confidence`
- Confidence: `low` (stale, conflicting sources)
- Citations: TRIAL-002 (stale, terminated), REPORT-002 (stale, superseded)
- Gaps: ["Stale evidence from 2019-2020", "TRIAL-002 was terminated for safety signal in different indication", "May not apply to current IPF development"]

### 3. Full refusal (insufficient evidence)
```
/triage "What evidence supports compound ZX-88 for treating pancreatic cancer?"
```

**Expected outcome:**
- Status: `refused`
- Answer: `null`
- Confidence: `none` (score 0.0)
- Citations: `[]`
- Gaps: ["No allowlisted evidence retrieved for this question."]

### 4. Hook denial tests (defensive layer)
Still in Claude Code, try:
```
Ask me to use WebFetch to fetch https://example.com
```
**Expected:** Denied by hook, reason: "WebFetch is disabled; evidence must come only from the local retriever"

```
Run `curl -s https://example.com` in Bash
```
**Expected:** Denied by hook, reason: "Command appears to perform outbound network access"

```
Run `ls` and `pytest -q`
```
**Expected:** Both allowed (no network pattern detected)

## Reviewing a result

After any `/triage` run, a `result_id` is returned. To flip it from `pending_review` to `approved`:

```bash
python -m triage review <result_id> --reviewer jsmith --decision approve --notes "Verified and approved"
```

This creates `results/<result_id>.review.json` and appends to `audit/log.jsonl`. Only this action makes a result "decision-usable".

## Audit trail

```bash
cat audit/log.jsonl | jq .
```

Every operation is logged: retrieval queries, grounding checks, confidence scores, results submitted, hook denials, and reviewer decisions. The log is append-only (immutable).

## File map

| Path | Purpose |
|---|---|
| `.claude/settings.json` | PreToolUse hook registration |
| `.claude/hooks/allowlist_guard.py` | Hook: denies WebFetch/WebSearch/Bash-network |
| `.claude/skills/triage/SKILL.md` | **Agent loop spec**: trigger, steps (6), stop conditions, handoff |
| `.mcp.json` | MCP server: stdio, runs `python3 -m mcp_server.server` |
| `allowlist.json` | **Source of truth**: which source_ids are approved |
| `reviewers.json` | **Source of truth**: valid reviewer ids |
| `corpus/docs/` | 11 synthetic documents (papers, patents, trials, reports) |
| `src/triage/` | Core modules: allowlist, corpus, retriever, confidence, grounding, audit, cli |
| `mcp_server/server.py` | **MCP server**: 5 tools (search, get_doc, validate, compute_confidence, submit) |
| `tests/` | 8 unit test modules (fully deterministic, no API/live session needed) |
| `audit/log.jsonl` | **Append-only audit log** (created at runtime) |
| `results/` | `<id>.json` (pipeline output) + `<id>.review.json` (reviewer decision) |

## Architecture summary

```
Human command: /triage <question>
  ↓ [Skill loads from .claude/skills/triage/SKILL.md]
  ↓ [Hook enforces allowlist on Bash/WebFetch/WebSearch]
  ├─ Step 1: mcp__triage-corpus__search_corpus(question)
  │   └─ Filters to allowlist, BM25-ranks, returns hits + search_id
  ├─ (zero hits) → refused → submit_result → handoff
  ├─ (hits found) → Agent drafts answer + cited_ids
  ├─ Step 3: mcp__triage-corpus__validate_citations(search_id, cited_ids)
  │   └─ Checks: allowlist + presence-in-hits (server-side)
  ├─ (invalid) → one retry allowed, then escalated → submit_result → handoff
  ├─ (valid) → Step 4: compute_confidence(citations)
  ├─ Step 5: submit_result(...)
  │   └─ Writes results/<id>.json with review_status=pending
  └─ Step 6: Handoff
      └─ Agent tells human: "pending_review" → must run `triage review` to finalize
```

## Extending

### Add a document
1. Create `corpus/docs/NEW-ID.json` with fields: source_id, source_type, title, date, org_or_venue, status, body
2. Add entry to `allowlist.json`: `{source_id, allowed, source_type, domain}`
3. Ensure invariant: if `status=retracted`, set `allowed=false`

### Change reviewers
Edit `reviewers.json`: add/remove `{id, name}` pairs.

### Adjust confidence formula
Edit `src/triage/confidence.py`: the `compute_confidence(citations)` function is pure, deterministic, and fully unit-testable.

### Adjust retriever parameters
Edit `src/triage/retriever.py`:
- `top_k` (default 6): number of hits to return
- `min_score` (default 0.15): normalized score threshold to include a hit
- BM25 parameters (`k1`, `b`) in `BM25Index.__init__`

### Add a new demo question
Just ask `/triage "<your question>"` in Claude Code. The skill handles the rest.

## Troubleshooting

### "Result not found" when reviewing
Confirm `result_id` from the triage output. Check `results/` directory:
```bash
ls -la results/
```

### "Unknown reviewer" when reviewing
Check `reviewers.json` for the reviewer's id. Valid ids: `jsmith`, `rjones`, `achen`.

### Hook is not blocking network calls
Ensure `.claude/settings.json` has the PreToolUse hook configured and `allowlist_guard.py` is executable:
```bash
chmod +x .claude/hooks/allowlist_guard.py
```

### MCP server won't start
Ensure `.mcp.json` has correct paths and `mcp` package is installed:
```bash
source .venv/bin/activate
pip install mcp
```

## One-minute test

```bash
./VERIFY.sh  # Confirms all 8 unit tests pass
```

If all pass, the system is ready for live agent testing.
