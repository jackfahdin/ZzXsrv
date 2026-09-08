@echo off
setlocal
call "%~dp0set-build-tools.bat"
"%PYTHON3%" %*
exit /b %errorlevel%
