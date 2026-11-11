@echo off
REM Start the Solana Desk on Windows. Double-click this file.
setlocal
cd /d "%~dp0"

set PORT=8000
if "%~1"=="" goto randomkey
if "%~1"=="--open" goto openkey
set DESK_TOKEN=%~1
goto deps

:randomkey
for /f "delims=" %%i in ('python -c "import secrets;print(secrets.token_urlsafe(18))"') do set DESK_TOKEN=%%i
goto deps

:openkey
set DESK_TOKEN=
echo ==============================================================
echo   WARNING: desk is OPEN. Anyone who can reach port %PORT%
echo   can read state and press Start / Reset / Kill.
echo ==============================================================

:deps
python -c "import fastapi, uvicorn, pydantic, requests" 2>nul
if errorlevel 1 (
  echo First run: installing dependencies, one time...
  python -m pip install --quiet -r requirements.txt
  if errorlevel 1 (
    echo ERROR: pip install failed. Install Python 3.10+ from python.org
    echo and tick "Add Python to PATH", then run this again.
    pause
    exit /b 1
  )
)

if not "%DESK_TOKEN%"=="" (
  echo ==============================================================
  echo   Solana Desk is LOCKED
  echo.
  echo   Open:  http://localhost:%PORT%
  echo   Key:   %DESK_TOKEN%
  echo.
  echo   On your phone: open the URL, then Pair this device.
  echo ==============================================================
)

python -m uvicorn app:app --host 0.0.0.0 --port %PORT%
pause
