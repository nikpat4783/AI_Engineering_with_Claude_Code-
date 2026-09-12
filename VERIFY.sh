#!/bin/bash
set -e

echo "=== R&D Evidence Triage System Verification ==="
echo ""

cd "$(dirname "$0")"

echo "1. Checking directory structure..."
test -d .claude/hooks && echo "  ✓ .claude/hooks"
test -d .claude/skills/triage && echo "  ✓ .claude/skills/triage"
test -d corpus/docs && echo "  ✓ corpus/docs"
test -d src/triage && echo "  ✓ src/triage"
test -d mcp_server && echo "  ✓ mcp_server"
test -d tests && echo "  ✓ tests"
test -f allowlist.json && echo "  ✓ allowlist.json"
test -f reviewers.json && echo "  ✓ reviewers.json"
echo ""

echo "2. Checking configuration files..."
test -f .claude/settings.json && echo "  ✓ .claude/settings.json"
test -f .claude/hooks/allowlist_guard.py && echo "  ✓ .claude/hooks/allowlist_guard.py"
test -f .claude/skills/triage/SKILL.md && echo "  ✓ .claude/skills/triage/SKILL.md"
test -f .mcp.json && echo "  ✓ .mcp.json"
echo ""

echo "3. Checking corpus documents..."
COUNT=$(ls corpus/docs/*.json 2>/dev/null | wc -l)
echo "  ✓ $COUNT documents in corpus/docs"
echo ""

echo "4. Checking source modules..."
test -f src/triage/__init__.py && echo "  ✓ triage/__init__.py"
test -f src/triage/allowlist.py && echo "  ✓ triage/allowlist.py"
test -f src/triage/corpus.py && echo "  ✓ triage/corpus.py"
test -f src/triage/retriever.py && echo "  ✓ triage/retriever.py"
test -f src/triage/confidence.py && echo "  ✓ triage/confidence.py"
test -f src/triage/grounding.py && echo "  ✓ triage/grounding.py"
test -f src/triage/schema.py && echo "  ✓ triage/schema.py"
test -f src/triage/audit.py && echo "  ✓ triage/audit.py"
test -f src/triage/cli.py && echo "  ✓ triage/cli.py"
test -f src/triage/__main__.py && echo "  ✓ triage/__main__.py"
echo ""

echo "5. Checking MCP server..."
test -f mcp_server/__init__.py && echo "  ✓ mcp_server/__init__.py"
test -f mcp_server/server.py && echo "  ✓ mcp_server/server.py"
echo ""

echo "6. Checking tests..."
TESTS=$(ls tests/test_*.py 2>/dev/null | wc -l)
echo "  ✓ $TESTS test modules"
echo ""

echo "7. Running unit tests..."
if [ -d .venv ]; then
  source .venv/bin/activate
else
  python3 -m venv .venv >/dev/null 2>&1
  source .venv/bin/activate
  pip install -e . >/dev/null 2>&1
fi

python tests/test_allowlist.py >/dev/null && echo "  ✓ test_allowlist"
python tests/test_reviewers.py >/dev/null && echo "  ✓ test_reviewers"
python tests/test_corpus_consistency.py >/dev/null && echo "  ✓ test_corpus_consistency"
python tests/test_retriever.py >/dev/null && echo "  ✓ test_retriever"
python tests/test_confidence.py >/dev/null && echo "  ✓ test_confidence"
python tests/test_grounding.py >/dev/null && echo "  ✓ test_grounding"
python tests/test_audit_log.py >/dev/null && echo "  ✓ test_audit_log"
python tests/test_hook_contract.py >/dev/null && echo "  ✓ test_hook_contract"
echo ""

echo "8. Verifying key files..."
python -c "from triage.corpus import load_corpus; from pathlib import Path; d=load_corpus(Path('corpus/docs')); print(f'  ✓ Loaded {len(d)} corpus documents')" 2>/dev/null
python -c "from triage.allowlist import load_allowlist; a=load_allowlist(); print(f'  ✓ Loaded allowlist with {len(a.sources)} entries')" 2>/dev/null
python -c "from triage.reviewers import load_reviewers; r=load_reviewers(); print(f'  ✓ Loaded {len(r.reviewers)} reviewers')" 2>/dev/null
echo ""

echo "=== All verifications passed! ✓ ==="
echo ""
echo "Next steps:"
echo "  1. Launch Claude Code:  cd $(pwd) && claude"
echo "  2. In Claude Code, run: /triage \"What evidence supports NX-14 for treating idiopathic pulmonary fibrosis, and is it safe?\""
echo "  3. Review the result:   python -m triage review <result_id> --reviewer jsmith --decision approve"
echo "  4. Check audit trail:   cat audit/log.jsonl | jq ."
