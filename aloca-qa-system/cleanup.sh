#!/bin/bash

# ALOCA+ QA System - Cleanup Script
# Removes build artifacts, logs, and temporary files

set -e

echo "🧹 ALOCA+ QA System Cleanup"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Track what was cleaned
cleaned_items=()

# Clean dist and build directories
if [ -d "./dist" ] || [ -d "./frontend/build" ] || [ -d "./frontend/.cache" ]; then
    echo "Removing build directories..."
    rm -rf ./dist ./frontend/build ./frontend/.cache 2>/dev/null || true
    cleaned_items+=("build directories")
    echo -e "${GREEN}✓ Cleaned dist, build, and cache directories${NC}"
fi

# Clean log files
if ls ./backend/*.log 1> /dev/null 2>&1 || ls ./frontend/*.log 1> /dev/null 2>&1; then
    echo "Removing log files..."
    rm -rf ./backend/*.log ./frontend/*.log 2>/dev/null || true
    cleaned_items+=("log files")
    echo -e "${GREEN}✓ Cleaned log files${NC}"
fi

# Clean OS files
if [ -f "./.DS_Store" ] || [ -f "./frontend/.DS_Store" ] || [ -f "./backend/.DS_Store" ]; then
    echo "Removing OS artifacts..."
    rm -f ./.DS_Store ./frontend/.DS_Store ./backend/.DS_Store 2>/dev/null || true
    cleaned_items+=("OS files")
    echo -e "${GREEN}✓ Cleaned OS artifacts${NC}"
fi

# Clean Python cache
if [ -d "./backend/__pycache__" ] || [ -d "./backend/.pytest_cache" ]; then
    echo "Removing Python cache..."
    rm -rf ./backend/__pycache__ ./backend/.pytest_cache 2>/dev/null || true
    cleaned_items+=("Python cache")
    echo -e "${GREEN}✓ Cleaned Python cache${NC}"
fi

echo ""
echo -e "${GREEN}✅ Cleanup completed!${NC}"
echo ""
echo "Cleaned items:"
for item in "${cleaned_items[@]}"; do
    echo "  • $item"
done
echo ""

# Optional: Show disk space saved (if du available)
if command -v du &> /dev/null; then
    echo "Current directory size:"
    du -sh . 2>/dev/null || echo "  (size calculation skipped)"
fi
