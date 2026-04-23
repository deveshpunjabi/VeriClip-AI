# VeriClip AI - Test Runner (PowerShell)
# Runs all test suites: unit, integration, adversarial

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  VeriClip AI - Test Suite" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Activate virtual environment if exists
$venvPath = Join-Path $PSScriptRoot "..\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
}

# Install test dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r (Join-Path $PSScriptRoot "..\backend\api\requirements.txt") -q

# Run unit tests
Write-Host "`nRunning unit tests..." -ForegroundColor Yellow
pytest (Join-Path $PSScriptRoot "..\tests\unit\") -v --tb=short

# Run integration tests
Write-Host "`nRunning integration tests..." -ForegroundColor Yellow
pytest (Join-Path $PSScriptRoot "..\tests\integration\") -v --tb=short

# Run adversarial tests
Write-Host "`nRunning adversarial tests..." -ForegroundColor Yellow
$advScript = Join-Path $PSScriptRoot "..\backend\tests\adversarial\simulate_attacks.py"
python $advScript

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "  All tests passed! " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
