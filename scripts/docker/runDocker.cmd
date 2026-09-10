@echo off
setlocal
for %%I in ("%~dp0..\..") do set "repoRoot=%%~fI"
docker run -m 4G -v "%repoRoot%:c:\src" -it vcxb
exit /b %errorlevel%
