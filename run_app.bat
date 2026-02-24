@echo off
echo Starting Legal Task Management Application...
echo.
echo Make sure you have set up your API keys in .env file before running.
echo.
cd /d "%~dp0"
python app.py
echo.
pause