@echo off
echo ===================================================
echo Starting AgriVision AI — Intelligent Crop Platform
echo ===================================================
"C:\Users\Gokul\AppData\Local\Programs\Python\Python310\python.exe" -m uvicorn agrivision.main:app --host 127.0.0.1 --port 8000 --reload
pause
