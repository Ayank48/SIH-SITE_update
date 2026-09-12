# TEAM ZERODAY: SIH26166 Lunar Image Correspondence Platform Launcher
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  TEAM ZERODAY // ISRO SIH26166 LUNAR CORRESPONDENCE PLATFORM   " -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan

$root = $PSScriptRoot
Set-Location $root

Write-Host "`n[1/2] Starting Python FastAPI Backend (Port 8000)..." -ForegroundColor Green
if (Test-Path "$root\.venv\Scripts\uvicorn.exe") {
	$backendProcess = Start-Process -FilePath "$root\.venv\Scripts\uvicorn.exe" -ArgumentList "backend.main:app --app-dir . --host 127.0.0.1 --port 8000 --reload" -PassThru -NoNewWindow
} else {
	$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn backend.main:app --app-dir `"$root`" --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory $root -PassThru -NoNewWindow
}

Start-Sleep -Seconds 3

Write-Host "`n[2/2] Starting Next.js Frontend Dashboard (Port 3000)..." -ForegroundColor Green
Set-Location "$root\frontend"
npm run dev
