# PowerShell Production Deployment Script for Vercel
# Run this script to deploy backend + dashboard to Vercel
# Usage: .\deploy.ps1

Write-Host "🚀 Spotify Review Analysis - Production Deployment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if Vercel CLI is installed
Write-Host "Checking Vercel CLI installation..." -ForegroundColor Yellow
if (-not (Get-Command "vercel" -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  Vercel CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g vercel
}

Write-Host "✅ Vercel CLI verified" -ForegroundColor Green

# Check if .env exists
Write-Host "Checking environment file..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env with the following variables:" -ForegroundColor Yellow
    Write-Host "  - DATABASE_URL" -ForegroundColor White
    Write-Host "  - SUPABASE_URL" -ForegroundColor White
    Write-Host "  - SUPABASE_KEY" -ForegroundColor White
    Write-Host "  - OPENAI_API_KEY" -ForegroundColor White
    exit 1
}

Write-Host "✅ Environment file found" -ForegroundColor Green

# Check if dashboard is built
Write-Host "Checking dashboard build..." -ForegroundColor Yellow
if (-not (Test-Path "dashboard/dist")) {
    Write-Host "⚠️  Dashboard not built. Building now..." -ForegroundColor Yellow
    Set-Location "dashboard"
    npm install
    npm run build
    Set-Location ".."
}

Write-Host "✅ Dashboard built" -ForegroundColor Green

# Deploy to Vercel
Write-Host ""
Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Cyan
vercel --prod

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update dashboard environment variables on Vercel:" -ForegroundColor White
Write-Host "   VITE_API_URL=https://your-app.vercel.app" -ForegroundColor White
Write-Host ""
Write-Host "2. Redeploy dashboard to use new API URL" -ForegroundColor White
Write-Host ""
Write-Host "3. Check dashboard at: https://your-app.vercel.app" -ForegroundColor White
Write-Host ""
