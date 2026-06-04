# Job Lister — Start backend + frontend
# Usage: .\start.ps1

$PYTHON = "C:\Users\Jeffrin\AppData\Local\Programs\Python\Python313\python.exe"
$ROOT = $PSScriptRoot

# Check ANTHROPIC_API_KEY
if (-not $env:ANTHROPIC_API_KEY) {
    Write-Host "WARNING: ANTHROPIC_API_KEY is not set. Cover letter generation will not work." -ForegroundColor Yellow
    Write-Host "Set it with: `$env:ANTHROPIC_API_KEY = 'your-key-here'" -ForegroundColor Yellow
    Write-Host ""
}

# Start backend
Write-Host "Starting FastAPI backend on http://localhost:8888 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT\backend'; & '$PYTHON' -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload"

Start-Sleep -Seconds 2

# Start frontend
Write-Host "Starting Next.js frontend on http://localhost:3000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT\frontend'; npm run dev"

Write-Host ""
Write-Host "Both servers starting. Open http://localhost:3000 in your browser." -ForegroundColor Green
