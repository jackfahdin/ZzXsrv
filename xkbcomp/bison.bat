@echo off
setlocal

cd /d "%~dp0"
call "%~dp0..\tools\set-build-tools.bat"

set "BISON_PKGDATADIR=%~dp0..\tools\mhmake\src\bisondata"

"%WIN_BISON%" %*

endlocal & exit /b %errorlevel%

