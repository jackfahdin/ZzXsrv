@echo off
rem Values are executable paths, without embedded quotes. scripts/build/buildall.ps1 sets
rem absolute paths; manual Developer Command Prompt builds may use PATH.
if not defined PYTHON3 set "PYTHON3=python.exe"
if not defined WIN_FLEX set "WIN_FLEX=win_flex.exe"
if not defined WIN_BISON set "WIN_BISON=win_bison.exe"
if not defined GPERF set "GPERF=gperf.exe"
