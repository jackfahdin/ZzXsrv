@echo off
setlocal
docker build -m 4G -t vcxb "%~dp0..\..\docker"
exit /b %errorlevel%
