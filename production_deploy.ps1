#!/usr/bin/env powershell
# RSS Feed Processor - Simple Production Deploy

param([int]$Days = 1, [switch]$DryRun)

Write-Host "RSS FEED PROCESSOR - PRODUCTION DEPLOYMENT" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "DRY RUN MODE - Testing system" -ForegroundColor Yellow
    python src/main.py --days $Days --dry-run
} else {
    Write-Host "PRODUCTION MODE - Sending emails" -ForegroundColor Green
    python src/main.py --days $Days
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: RSS Feed Processor completed!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Process failed with code $LASTEXITCODE" -ForegroundColor Red
}
