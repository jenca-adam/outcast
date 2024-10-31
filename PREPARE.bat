@echo off
echo Installing required packages...

python -m pip install -r requirements.txt >nul
if %errorlevel% neq 0 (
    echo pip install failed. Check console for details.
    exit /b %errorlevel%
)

echo Compiling cCore.pyd extension module...

python setup.py build_ext -i >nul
if %errorlevel% neq 0 (
    echo Compilation failed. Ensure that you have a working c compiler and python header files. 
    exit /b %errorlevel%
)

rd /s /q build
