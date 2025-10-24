# PowerShell script to install translation dependency
# Run this in PowerShell: .\setup_translation.ps1

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Setting Up Multi-Language Translation" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Uninstall old problematic package if exists
Write-Host "Removing old translation package (if exists)..." -ForegroundColor Yellow
pip uninstall googletrans -y 2>$null

# Install deep-translator for translation
Write-Host "Installing deep-translator for multi-language support..." -ForegroundColor Cyan
pip install deep-translator --upgrade

# Fix httpx conflicts
Write-Host "Upgrading httpx to fix dependency conflicts..." -ForegroundColor Cyan
pip install httpx --upgrade

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now use the translation feature!" -ForegroundColor Yellow
Write-Host ""
Write-Host "To test:" -ForegroundColor Yellow
Write-Host "  cd precision_agronomist" -ForegroundColor White
Write-Host "  crewai run" -ForegroundColor White
Write-Host ""
Write-Host "Supported languages: English, Spanish, Hindi, French, Portuguese," -ForegroundColor Cyan
Write-Host "Chinese, Arabic, Bengali, German, Japanese, Punjabi, and more!" -ForegroundColor Cyan
Write-Host ""

