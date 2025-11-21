#!/bin/bash

# Backend Test Runner Script
echo "Running CineForge AI Backend Tests..."

# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest tests/

# Run specific test categories
# pytest tests/ -m unit          # Run only unit tests
# pytest tests/ -m integration   # Run only integration tests
# pytest tests/ -m e2e           # Run only e2e tests

# Run with coverage
# pytest tests/ --cov=. --cov-report=html

echo "Tests completed!"
