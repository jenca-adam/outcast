@echo off
set OUTCAST_PYTHON=python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Make sure Python is installed and added to PATH.
    exit /B 1
)

echo Using Python at: %OUTCAST_PYTHON%
%OUTCAST_PYTHON% -m PyInstaller freeze.spec --noconfirm
rd /s /q build
