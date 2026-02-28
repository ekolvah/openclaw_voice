@echo off
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-cpu.txt
echo.
echo Ready. Copy .env.example to .env, fill keys, then run run.bat
pause
