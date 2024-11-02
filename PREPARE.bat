@echo off
set OUTCAST_PYTHON=python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Make sure Python is installed and added to PATH.
    exit /B 1
)

echo Python is: %OUTCAST_PYTHON%
echo Installing required packages...
%OUTCAST_PYTHON% -m pip install -r requirements.txt >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo pip install failed with returncode %ERRORLEVEL%
    exit /B 1
)

echo Compiling cCore.so extension module...
%OUTCAST_PYTHON% setup.py build_ext -i >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo compile failed with returncode %ERRORLEVEL%, are you on Windows?
    exit /B 1
)

rd /s /q build
echo Compiling using pyinstaller...
call PYI_FREEZE.bat
call PACK.bat
