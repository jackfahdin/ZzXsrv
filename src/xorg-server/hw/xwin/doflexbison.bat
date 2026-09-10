@echo off
setlocal

cd /d "%~dp0"
call "%~dp0..\..\..\..\tools\set-build-tools.bat"

set "BISON_PKGDATADIR=%~dp0..\..\..\..\tools\mhmake\src\bisondata"

"%WIN_BISON%" -d -o%1/winprefsyacc.c winprefsyacc.y
if errorlevel 1 exit /b %errorlevel%

"%WIN_FLEX%" -i -o%1/winprefslex.c winprefslex.l

endlocal & exit /b %errorlevel%

