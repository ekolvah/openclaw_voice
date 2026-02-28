@echo off
if not exist .venv\Scripts\activate.bat (
  echo Missing virtual environment. Run install.bat first.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python voice_bridge.py
pause
