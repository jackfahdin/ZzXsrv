#!/bin/bash

# ZzXsrv 只发布 64 位 Release：32 位与 debug 安装脚本已随品牌化移除

rm -f zzxsrv-64.*.installer*.exe

cp "$VCToolsRedistDir/x64/Microsoft.VC143.CRT/msvcp140.dll" .
cp "$VCToolsRedistDir/x64/Microsoft.VC143.CRT/vcruntime140.dll" .
cp "$VCToolsRedistDir/x64/Microsoft.VC143.CRT/vcruntime140_1.dll" .

if [[ -f "/mnt/c/Program Files (x86)/NSIS/makensis.exe" ]]; then
	if [[ -f ../obj64/servrelease/ZzXsrv.exe ]]; then
    "/mnt/c/Program Files (x86)/NSIS/makensis.exe" zzxsrv-64.nsi
  fi
else
	if [[ -f ../obj64/servrelease/ZzXsrv.exe ]]; then
	  "/mnt/c/Program Files/NSIS/makensis.exe" zzxsrv-64.nsi
  fi
fi
patch -p3 < noadmin.patch
if [[ -f "/mnt/c/Program Files (x86)/NSIS/makensis.exe" ]]; then
	if [[ -f ../obj64/servrelease/ZzXsrv.exe ]]; then
    "/mnt/c/Program Files (x86)/NSIS/makensis.exe" zzxsrv-64.nsi
  fi
else
	if [[ -f ../obj64/servrelease/ZzXsrv.exe ]]; then
	  "/mnt/c/Program Files/NSIS/makensis.exe" zzxsrv-64.nsi
  fi
fi
patch -p3 -R < noadmin.patch

rm -f vcruntime140.dll
rm -f msvcp140.dll
rm -f vcruntime140_1.dll
