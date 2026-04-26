@echo off
REM Backend startup script for Windows
REM Runs without --reload to prevent file watching issues on Windows
REM Use this for stable local development

echo Starting Financial Intelligence System Backend (Windows)
echo Running without --reload for stability...

C:\Python313\python.exe -m uvicorn api:app --host 0.0.0.0 --port 8000

pause
