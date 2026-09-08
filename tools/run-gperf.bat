@echo off
setlocal
call "%~dp0set-build-tools.bat"
"%GPERF%" %*
exit /b %errorlevel%
