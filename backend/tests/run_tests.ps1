# PowerShell Test Runner Script
Write-Host "Running CineForge AI Backend Tests..." -ForegroundColor Cyan

# Install test dependencies
Write-Host "Installing test dependencies..." -ForegroundColor Yellow
pip install -r tests/requirements.txt

# Run all tests
Write-Host "Running tests..." -ForegroundColor Yellow
pytest tests/ -v

# Uncomment to run specific test categories:
# pytest tests/ -m unit          # Run only unit tests
# pytest tests/ -m integration   # Run only integration tests  
# pytest tests/ -m e2e           # Run only e2e tests

# Uncomment to run with coverage:
# pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

Write-Host "Tests completed!" -ForegroundColor Green
