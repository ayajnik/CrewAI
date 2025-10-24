# PowerShell script to deploy to CrewAI AMP
# Run this in PowerShell: .\deploy_amp.ps1

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Deploying Precision Agronomist to CrewAI AMP" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Check if amp.yaml exists
if (-not (Test-Path "amp.yaml")) {
    Write-Host "❌ amp.yaml not found! Please create it first." -ForegroundColor Red
    exit 1
}

# Install AMP CLI if not available
Write-Host "Checking CrewAI AMP CLI..." -ForegroundColor Cyan
try {
    crewai amp --help | Out-Null
    Write-Host "✅ AMP CLI found" -ForegroundColor Green
} catch {
    Write-Host "Installing CrewAI with AMP support..." -ForegroundColor Yellow
    pip install 'crewai[tools]' --upgrade
}

# Login to AMP (if not already logged in)
Write-Host "Authenticating with CrewAI AMP..." -ForegroundColor Cyan
crewai amp login

# Validate configuration
Write-Host "Validating AMP configuration..." -ForegroundColor Cyan
crewai amp validate

# Deploy to AMP
Write-Host "Deploying to CrewAI AMP..." -ForegroundColor Cyan
crewai amp deploy

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your crew is now deployed to CrewAI AMP!" -ForegroundColor Yellow
Write-Host "Check the dashboard for your API endpoints." -ForegroundColor Yellow
Write-Host ""
