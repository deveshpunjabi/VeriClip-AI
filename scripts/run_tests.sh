#!/bin/bash
# VeriClip AI - Test Runner
# Runs all test suites: unit, integration, adversarial, and load tests

set -e

echo "=========================================="
echo "  VeriClip AI - Test Suite"
echo "=========================================="

# Activate virtual environment if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "backend/.venv" ]; then
    source backend/.venv/bin/activate
fi

# Install test dependencies
echo "Installing dependencies..."
pip install -r backend/api/requirements.txt -q

# Run unit tests
echo ""
echo "▶ Running unit tests..."
pytest tests/unit/ -v --tb=short

# Run integration tests
echo ""
echo "▶ Running integration tests..."
pytest tests/integration/ -v --tb=short

# Run adversarial tests
echo ""
echo "▶ Running adversarial tests..."
python backend/tests/adversarial/simulate_attacks.py

echo ""
echo "=========================================="
echo "  All tests passed! ✓"
echo "=========================================="
