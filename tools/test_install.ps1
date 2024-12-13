# TRAA Installation Test Script for Windows
Write-Host "`n=== TRAA Installation Test ===`n" -ForegroundColor Green

# Create a temporary virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Green
python -m venv test_venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create virtual environment!" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Green
.\test_venv\Scripts\Activate.ps1
if (-not $?) {
    Write-Host "Failed to activate virtual environment!" -ForegroundColor Red
    exit 1
}

try {
    # Install build dependencies
    Write-Host "`nInstalling build dependencies..." -ForegroundColor Green
    pip install --upgrade pip wheel setuptools
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install build dependencies!"
    }

    # Test development installation
    Write-Host "`nTesting development installation..." -ForegroundColor Green
    pip install -e .
    if ($LASTEXITCODE -ne 0) {
        throw "Development installation failed!"
    }
    
    python tools/test_install.py
    if ($LASTEXITCODE -ne 0) {
        throw "Development installation tests failed!"
    }
    
    pip uninstall -y traa
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to uninstall development package!"
    }

    # Clean build artifacts
    Write-Host "`nCleaning build artifacts..." -ForegroundColor Green
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build/,dist/,*.egg-info/

    # Test regular installation
    Write-Host "`nTesting regular installation..." -ForegroundColor Green
    pip install .
    if ($LASTEXITCODE -ne 0) {
        throw "Regular installation failed!"
    }
    
    python tools/test_install.py
    if ($LASTEXITCODE -ne 0) {
        throw "Regular installation tests failed!"
    }

    Write-Host "`nInstallation tests completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "`nError: $_" -ForegroundColor Red
    exit 1
}
finally {
    # Clean up
    Write-Host "`nCleaning up..." -ForegroundColor Green
    deactivate
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue test_venv/
} 