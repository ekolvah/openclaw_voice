@echo off
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher "py" not found. Install Python 3.12 from python.org.
  pause
  exit /b 1
)

py -3.12 -c "import sys; print(sys.version)" >nul 2>nul
if errorlevel 1 (
  echo Python 3.12 is required but not found.
  echo Install Python 3.12 and rerun install.bat
  pause
  exit /b 1
)

if exist .venv (
  rmdir /s /q .venv
)

py -3.12 -m venv .venv
if errorlevel 1 goto :fail

.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :fail

.venv\Scripts\python.exe -m pip install -e ".[dev]"
if errorlevel 1 goto :fail

.venv\Scripts\python.exe -m pip install -r requirements-cpu.txt
if errorlevel 1 goto :fail

echo.
echo Ready. Copy .env.example to .env, fill keys, then run run.bat
pause
exit /b 0

:fail
echo.
echo Installation failed. Fix the error above and run install.bat again.
pause
exit /b 1
