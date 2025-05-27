# RSS Feed Processor - Production Deployment Script
# Run this for daily news digest production deployment

param(
    [int]$Days = 1,
    [switch]$DryRun,
    [switch]$Test,
    [switch]$Verify
)

Write-Host "🚀 RSS FEED PROCESSOR - PRODUCTION DEPLOYMENT" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "src/main.py")) {
    Write-Host "❌ Error: Must run from RSS Feed Processor root directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Verification mode
if ($Verify) {
    Write-Host "🔍 Running production verification..." -ForegroundColor Yellow
    python production_verification.py
    exit 0
}

# Test mode
if ($Test) {
    Write-Host "🧪 Running quick system test..." -ForegroundColor Yellow
    python simple_test.py
    exit 0
}

# Production deployment
$dayText = if ($Days -gt 1) { "s" } else { "" }
Write-Host "📅 Processing news for the last $Days day$dayText" -ForegroundColor Green

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No emails will be sent" -ForegroundColor Yellow
    python src/main.py --days $Days --dry-run
} else {
    Write-Host "📧 PRODUCTION MODE - Emails will be sent" -ForegroundColor Green
    python src/main.py --days $Days
}

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ RSS Feed Processor completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ RSS Feed Processor encountered an error (Exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "🎯 Next scheduled run: Tomorrow at the same time" -ForegroundColor Cyan
