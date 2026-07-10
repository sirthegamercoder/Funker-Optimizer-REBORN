@echo off
cd /d "%~dp0"
echo.
echo Install requirements
pip install -r requirements.txt
echo.
echo Requirements has installed!
exit /b