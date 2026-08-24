/*  This file is part of vcxsrv.
 *
 *  Copyright (C) 2024 https://github.com/marchaesen
 *
 *  vcxsrv is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  vcxsrv is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with vcxsrv.  If not, see <http://www.gnu.org/licenses/>.
*/
;--------------------------------
!include "FileFunc.nsh"

!define NAME "ZzXsrv"
!define VERSION "21.1.16.1"
!define UNINSTALL_PUBLISHER "${NAME}"
!define UNINSTALL_URL "https://github.com/jackfahdin/ZzXsrv"

; The name of the installer
Name "${NAME}"

; The file to write
OutFile "zzxsrv-64.${VERSION}.installer.exe"

; The default installation directory
InstallDir $programfiles64\ZzXsrv

SetCompressor /SOLID lzma

; Registry key to check for directory (so if you install again, it will
; overwrite the old one automatically)
InstallDirRegKey HKLM SOFTWARE\ZzXsrv "Install_Dir_64"

LoadLanguageFile "${NSISDIR}\Contrib\Language files\English.nlf"

VIProductVersion "${VERSION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${NAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "ZzXsrv windows xserver"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${VERSION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductVersion" "${VERSION}"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------
InstType "Full"
InstType "Minimal"

; Pages

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

SetPluginUnload alwaysoff
; ShowInstDetails show
XPStyle on

!define FUSION_REFCOUNT_UNINSTALL_SUBKEY_GUID {8cedc215-ac4b-488b-93c0-a50a49cb2fb8}

;--------------------------------
; The stuff to install
Section "ZzXsrv (required)"

  SetShellVarContext All

  SectionIn RO
  SectionIn 1 2 3

  SetRegView 64

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR

  ; Remove old opengl32.dll file if it extits
  IfFileExists "$INSTDIR\opengl32.dll" 0 +2
    Delete "$INSTDIR\opengl32.dll"
  IfFileExists "$INSTDIR\msvcr100.dll" 0 +2
    Delete "$INSTDIR\msvcr100.dll"
  IfFileExists "$INSTDIR\msvcp100.dll" 0 +2
    Delete "$INSTDIR\msvcp100.dll"
  IfFileExists "$INSTDIR\msvcr110.dll" 0 +2
    Delete "$INSTDIR\msvcr110.dll"
  IfFileExists "$INSTDIR\msvcp110.dll" 0 +2
    Delete "$INSTDIR\msvcp110.dll"
  IfFileExists "$INSTDIR\msvcrt120.dll" 0 +2
    Delete "$INSTDIR\msvcrt120.dll"
  IfFileExists "$INSTDIR\msvcp120.dll" 0 +2
    Delete "$INSTDIR\msvcp120.dll"

  ; Put files there
  File "..\obj64\servrelease\ZzXsrv.exe"
  File "..\dix\protocol.txt"
  File "..\system.XWinrc"
  File "..\X0.hosts"
  File "..\..\xkbcomp\obj64\release\xkbcomp.exe"
  File "..\XKeysymDB"
  File "..\..\libX11\src\XErrorDB"
  File "..\..\libX11\src\xcms\Xcms.txt"
  File "..\XtErrorDB"
  File "..\font-dirs"
  File "..\.Xdefaults"
  File "..\..\libxml2\bin64\libxml2-2.dll"
  File "..\..\libxml2\bin64\libgcc_s_sjlj-1.dll"
  File "..\..\libxml2\bin64\libiconv-2.dll"
  File "..\..\libxml2\bin64\libwinpthread-1.dll"
  File "..\..\zlib\obj64\release\zlib1.dll"
  File "..\..\libxcb\src\obj64\release\libxcb.dll"
  File "..\..\libXau\obj64\release\libXau.dll"
  File "..\..\libX11\obj64\release\libX11.dll"
  File "..\..\openssl\release64\libcrypto-3-x64.dll"
  File "..\..\freetype\objs\x64\Release\freetype.dll"
  File "vcruntime140.dll"
  File "vcruntime140_1.dll"
  File "msvcp140.dll"
  SetOutPath $INSTDIR\xkbdata
  File /r "..\xkbdata\*.*"
  SetOutPath $INSTDIR\locale
  File /r "..\locale\*.*"
  SetOutPath $INSTDIR\bitmaps
  File /r "..\bitmaps\*.*"

  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\ZzXsrv "Install_Dir_64" "$INSTDIR"

  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZzXsrv" "DisplayIcon" "$INSTDIR\ZzXsrv.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZzXsrv" "DisplayName" "${NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZzXsrv" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZzXsrv" "Publisher" "https://github.com/jackfahdin/ZzXsrv"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZzXsrv" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZzXsrv" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZzXsrv" "NoRepair" 1
  WriteUninstaller "uninstall.exe"

  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZzXsrv" "EstimatedSize" "$0"

SectionEnd

; Optional section (can be disabled by the user)
Section "Fonts"
  SectionIn 1 3

  SetShellVarContext All

  SetRegView 64

  SetOutPath $INSTDIR\fonts
  CreateDirectory "$INSTDIR\fonts"
  File /r "..\fonts\*.*"

SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"
  SectionIn 1 3

  SetShellVarContext All

  SetRegView 64

  SetOutPath "$SMPROGRAMS\ZzXsrv"
  CreateDirectory "$SMPROGRAMS\ZzXsrv"
  CreateShortCut "$SMPROGRAMS\ZzXsrv\ZzXsrv.lnk" "$INSTDIR\ZzXsrv.exe" "" "$INSTDIR\ZzXsrv.exe" 0
  CreateShortCut "$SMPROGRAMS\ZzXsrv\Uninstall ZzXsrv.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"

  SetRegView 64

  SetShellVarContext All

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZzXsrv"
  DeleteRegKey HKLM SOFTWARE\ZzXsrv

  ; Remove files and uninstaller
  Delete "$INSTDIR\ZzXsrv.exe"
  Delete "$INSTDIR\uninstall.exe"
  Delete "$INSTDIR\protocol.txt"
  Delete "$INSTDIR\system.XWinrc"
  Delete "$INSTDIR\xkbcomp.exe"
  Delete "$INSTDIR\XKeysymDB"
  Delete "$INSTDIR\XErrorDB"
  Delete "$INSTDIR\Xcms.txt"
  Delete "$INSTDIR\XtErrorDB"
  Delete "$INSTDIR\font-dirs"
  Delete "$INSTDIR\.Xdefaults"
  Delete "$INSTDIR\libxcb.dll"
  Delete "$INSTDIR\libXau.dll"
  Delete "$INSTDIR\libX11.dll"
  Delete "$INSTDIR\libxml2.dll"
  Delete "$INSTDIR\zlib1.dll"
  Delete "$INSTDIR\iconv.dll"
  Delete "$INSTDIR\vcruntime140.dll"
  Delete "$INSTDIR\vcruntime140_1.dll"
  Delete "$INSTDIR\msvcp140.dll"
  Delete "$INSTDIR\vcruntime140d.dll"
  Delete "$INSTDIR\vcruntime140_1d.dll"
  Delete "$INSTDIR\msvcp140d.dll"
  Delete "$INSTDIR\libgcc_s_sjlj-1.dll"
  Delete "$INSTDIR\libcrypto-1_1-x64.dll"
  Delete "$INSTDIR\libiconv-2.dll"
  Delete "$INSTDIR\libwinpthread-1.dll"
  Delete "$INSTDIR\libxml2-2.dll"
  Delete "$INSTDIR\X0.hosts"


  RMDir /r "$INSTDIR\fonts"
  RMDir /r "$INSTDIR\xkbdata"
  RMDir /r "$INSTDIR\locale"
  RMDir /r "$INSTDIR\bitmaps"

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\ZzXsrv\*.*"

  ; Remove directories used
  RMDir "$SMPROGRAMS\ZzXsrv"
  RMDir "$INSTDIR"

SectionEnd
