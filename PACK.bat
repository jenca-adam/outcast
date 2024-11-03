@echo off
if not exist "dist\outcast" (
    echo Please run PYI_FREEZE.bat first
    exit /B 1
)

echo Preparing pack operation...
del dist\OUTCAST*tar.gz >nul 2>&1

for /f "tokens=*" %%i in (files\VERSION) do set VERSION=%%i
for /f "tokens=2 delims=." %%j in ('dir /b /s dist\outcast\cCore.*.pyd') do set CORE_VERSION=%%j
set FN=OUTCAST.%VERSION%.%CORE_VERSION%.tar

echo Packing with tar...
echo Filename: dist\%FN%
cd dist
tar -cf %FN% *
echo Gzipping...
gzip -f %FN%
echo Cleaning up...
rd /s /q outcast
move *.tar.gz ..\gzipped_dist
cd ..
rd /s /q dist
