$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "Starting services from: $root" -ForegroundColor Cyan
Write-Host "Browser: http://localhost:5173" -ForegroundColor Green
Write-Host ""

$q = "'$($root -replace "'", "''")'"

# Planning :8000
$c1 = "cd $q; cd planning-service; Write-Host 'Planning :8000' -ForegroundColor Yellow; pip install -q -r requirements.txt; uvicorn main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $c1

Start-Sleep -Seconds 5

# Operations :8001
$c2 = "cd $q; cd operations-service; Write-Host 'Operations :8001' -ForegroundColor Yellow; `$env:PLANNING_SERVICE_URL='http://localhost:8000'; pip install -q -r requirements.txt; uvicorn main:app --reload --port 8001"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $c2

Start-Sleep -Seconds 4

# Analytics :8002
$c3 = "cd $q; cd analytics-service; Write-Host 'Analytics :8002' -ForegroundColor Yellow; `$env:OPERATIONS_SERVICE_URL='http://localhost:8001'; `$env:PLANNING_SERVICE_URL='http://localhost:8000'; pip install -q -r requirements.txt; uvicorn main:app --reload --port 8002"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $c3

Start-Sleep -Seconds 4

# Frontend :5173
$c4 = "cd $q; cd frontend; Write-Host 'Frontend :5173' -ForegroundColor Yellow; if (-not (Test-Path node_modules)) { npm install }; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $c4

Write-Host "Four windows opened. Close them to stop. Site: http://localhost:5173" -ForegroundColor Cyan
