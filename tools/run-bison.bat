@echo off
setlocal
call "%~dp0set-build-tools.bat"
"%WIN_BISON%" %*
exit /b %errorlevel%
