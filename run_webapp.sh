#!/bin/bash
set -e

echo "=================================="
echo "Evidence Triage Web UI"
echo "=================================="
echo ""

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies..."
pip install -q -e ".[web]"

echo ""
echo "✓ Setup complete!"
echo ""
echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop."
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:8000 in your browser"
echo "  2. Paste your Groq API key (gsk_...)"
echo "  3. Try an example question or ask your own"
echo ""

uvicorn webapp.server:app --reload --port 8000
