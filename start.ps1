Write-Host "===================================================" -ForegroundColor Green
Write-Host "Starting AgriVision AI — Intelligent Crop Platform" -ForegroundColor Cyan
Write-Host "Interactive UI available at: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "API Documentation at:        http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Green

& "C:\Users\Gokul\AppData\Local\Programs\Python\Python310\python.exe" -m uvicorn agrivision.main:app --host 127.0.0.1 --port 8000 --reload
