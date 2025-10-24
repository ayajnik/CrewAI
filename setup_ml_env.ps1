# Setup script for ML environment (Python 3.12)
# Run this to create a separate environment for TensorFlow/YOLO

Write-Host "Creating Python 3.12 virtual environment for ML models..." -ForegroundColor Cyan

# Check if Python 3.12 is available
$python312 = $null
$pythonPaths = @("py -3.12", "python3.12", "python")

foreach ($pyCmd in $pythonPaths) {
    try {
        $version = & $pyCmd --version 2>&1
        if ($version -match "3\.12") {
            $python312 = $pyCmd
            Write-Host "Found Python 3.12: $python312" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if (-not $python312) {
    Write-Host "ERROR: Python 3.12 not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.12 from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "You can have multiple Python versions installed." -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
& $python312 -m venv ml_env

# Activate and install dependencies
Write-Host "Installing ML dependencies..." -ForegroundColor Cyan
& .\ml_env\Scripts\Activate.ps1

pip install --upgrade pip
pip install tensorflow==2.17.0
pip install ultralytics
pip install opencv-python
pip install numpy
pip install pillow

Write-Host ""
Write-Host "✅ ML environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "The environment is located at: ml_env\" -ForegroundColor Cyan
Write-Host "Python executable: ml_env\Scripts\python.exe" -ForegroundColor Cyan

