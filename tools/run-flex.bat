@echo off
setlocal
call "%~dp0set-build-tools.bat"
"%WIN_FLEX%" %*
exit /b %errorlevel%
