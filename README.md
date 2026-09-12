# R&D Evidence Triage Agent

A Claude Code–native agentic system for triaging research questions against an allowlisted corpus of papers, patents, trial registries, and internal reports. Returns structured, grounded, confidence-scored evidence — with a required human reviewer gate before any decision use.

## Four commitments

1. **Retrieve only from approved sources** — enforced by PreToolUse hook (denying WebFetch/WebSearch) and MCP server (structurally filtering to allowlist)
2. **Ground every claim** — every citation is checked against the actual retrieved evidence set
3. **Return structured output** — answer, confidence (computed, not LLM vibes), citations, gaps
4. **Fail gracefully** — refuse or escalate rather than fabricate; all results pending human review

## Quick start

```bash
cd /home/labuser/Downloads/RAG_AGENTIC_SCIENTIFIC
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Run tests (no live agent needed)

```bash
python3 -m pytest tests/ -v
```

All tests pass without requiring ANTHROPIC_API_KEY or a live Claude Code session.

### Run demo in Claude Code

```bash
claude  # launch Claude Code in this directory
```

In the Claude Code session:

```
/triage "What evidence supports NX-14 for treating idiopathic pulmonary fibrosis, and is it safe?"
```

Expected result: `pending_review`, citing PAPER-001/002, TRIAL-001, REPORT-001, high/medium confidence.

### Review a result

```bash
python -m triage review <result_id> --reviewer jsmith --decision approve --notes "Looks good"
```

This is the only way a result becomes "decision-usable" — review produces `<result_id>.review.json` and appends to the audit log.

### Inspect the audit trail

```bash
cat audit/log.jsonl | jq .
```

## Files

- **`.claude/settings.json`** — PreToolUse hook registration (denies WebFetch/WebSearch/Bash-network)
- **`.claude/hooks/allowlist_guard.py`** — hook implementation
- **`.claude/skills/triage/SKILL.md`** — the agent-loop specification (trigger, steps, tools, stop conditions, handoff)
- **`.mcp.json`** — MCP server registration (stdio, runs `python3 -m mcp_server.server`)
- **`allowlist.json`** — single source of truth: which source_ids are approved
- **`reviewers.json`** — who can approve results (id, name pairs)
- **`corpus/docs/`** — 11 synthetic documents (papers, patents, trials, reports)
- **`src/triage/`** — core modules (allowlist, corpus, retriever, confidence, grounding, audit, CLI)
- **`mcp_server/`** — MCP server exposing 4 tools (search_corpus, get_document, validate_citations, compute_confidence, submit_result)
- **`tests/`** — unit tests (allowlist, retriever, confidence, grounding, corpus consistency, audit log, reviewers, hook contract)

## Corpus scenario

A fictional compound **NX-14 ("Nexafib")**, a ROCK2 inhibitor for idiopathic pulmonary fibrosis (IPF).

| source_id | type | status | allowed | role |
|---|---|---|---|---|
| PAPER-001/002 | paper | active | yes | strong, corroborating efficacy/safety evidence |
| PAPER-003 | paper | active | **no** | predatory-journal piece — never surfaces |
| PATENT-001 | patent | active | yes | tests "claimed" vs "demonstrated" |
| TRIAL-001 | trial | active | yes | corroborates PAPER-002 |
| TRIAL-002 | trial | **stale** | yes | old, terminated, different indication — low-confidence driver |
| TRIAL-003 | trial | active | **no** | unverifiable third-party mirror |
| REPORT-001 | internal | active | yes | current safety memo, no signal |
| REPORT-002 | internal | **stale** | yes | superseded 2019 memo — low-confidence driver |
| REPORT-003 | internal | **retracted** | **no** | pulled for data-integrity issue |

Demo scenarios:
- **Confident/grounded**: "What evidence supports NX-14 for IPF, and is it safe?" → high/medium confidence, 4 citations.
- **Low-confidence/gaps**: "Are there safety concerns about NX-14 across indications?" → low confidence, gaps name the stale/conflicting evidence.
- **Refused**: "What evidence supports ZX-88 for pancreatic cancer?" → zero hits above threshold.

## Architecture

```
human: /triage "<question>"
  ↓ mcp__triage-corpus__search_corpus(question)
  ├─ zero hits → refused → submit_result → handoff
  └─ hits found ↓
    (agent drafts answer + cited_ids, constrained by SKILL.md)
    ↓ mcp__triage-corpus__validate_citations(search_id, cited_ids)
    ├─ valid → compute_confidence → submit_result → handoff
    ├─ invalid (1st retry allowed)
    │  └─ still invalid → escalated → submit_result → handoff
    └─ (hook denies WebFetch/WebSearch/Bash-network throughout)
```

All output is `pending_review` until a named reviewer approves via:
```bash
python -m triage review <result_id> --reviewer <id> --decision approve|reject
```

## Extending

- **Add documents**: Drop JSON files into `corpus/docs/`, add entries to `allowlist.json`.
- **Change reviewers**: Edit `reviewers.json`.
- **Modify confidence formula**: Edit `src/triage/confidence.py` (pure function, fully testable).
- **Adjust retriever**: Edit `src/triage/retriever.py` (BM25 parameters, min_score threshold).

## Testing checklist

```bash
# Unit tests (no API key needed)
pytest tests/ -v

# Specific test module
pytest tests/test_retriever.py -v

# Hook contract (subprocess the hook directly)
python tests/test_hook_contract.py

# Live agent (requires Claude Code session + ANTHROPIC_API_KEY)
# /triage "What evidence supports NX-14 for IPF, and is it safe?"
# /triage "Are there safety concerns about NX-14 across indications?"
# /triage "What evidence supports ZX-88 for pancreatic cancer?"

# Review a result
python -m triage review <result_id> --reviewer jsmith --decision approve

# Inspect audit trail
cat audit/log.jsonl | jq .
```

## References

- Plan: `.claude/plans/r-d-teams-draw-on-calm-emerson.md`
- Skill: `.claude/skills/triage/SKILL.md`
- Hook: `.claude/hooks/allowlist_guard.py`
- MCP server: `mcp_server/server.py`
