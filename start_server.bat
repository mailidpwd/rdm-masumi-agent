@echo off
echo ======================================================================
echo   Starting RDM API Server with Masumi Integration
echo ======================================================================
echo.

cd /d "%~dp0"
.\.venv311\Scripts\python.exe main.py api

pause


