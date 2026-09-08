@echo off
setlocal

cd /d "%~dp0"
call "%~dp0..\set-build-tools.bat"
"%WIN_FLEX%" --nounistd -Ssrc/flex.skl -o%1/mhmakelexer.cpp src/mhmakelexer.l
if errorlevel 1 exit /b %errorlevel%

"%PYTHON3%" addstdafxh.py %1\mhmakelexer.cpp

endlocal & exit /b %errorlevel%

