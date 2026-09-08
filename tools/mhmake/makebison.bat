@echo off
setlocal

cd /d "%~dp0"
call "%~dp0..\set-build-tools.bat"
set "BISON_PKGDATADIR=%~dp0src\bisondata"

"%WIN_BISON%" -d -Ssrc/bisondata/skeletons/lalr1.cc -o%1/mhmakeparser.cpp src\mhmakeParser.y
if errorlevel 1 exit /b %errorlevel%
"%PYTHON3%" addstdafxh.py %1\mhmakeparser.cpp

endlocal & exit /b %errorlevel%
