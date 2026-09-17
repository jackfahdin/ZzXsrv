; ZzXsrv x64 installer (Inno Setup 7)
; Build via tools/package_release.py, which passes:
;   /DZxVersion=... /DZxDistDir=... /DZxOutDir=... [/DZxOutName=...]

#ifndef ZxVersion
  #define ZxVersion "2026.9.17"
#endif
#ifndef ZxDistDir
  #define ZxDistDir "dist\x64\Release"
#endif
#ifndef ZxOutDir
  #define ZxOutDir "dist\release"
#endif
#ifndef ZxOutName
  #define ZxOutName "zzxsrv-" + ZxVersion + "-x64-setup"
#endif
#ifndef ZxLicenseFile
  #define ZxLicenseFile "COPYING"
#endif

[Setup]
AppId={{7E5A3C21-9B4D-4E6F-A1C8-2D5F7B9E0A31}
AppName=ZzXsrv
AppVersion={#ZxVersion}
AppVerName=ZzXsrv {#ZxVersion}
AppPublisher=ZzXsrv
AppPublisherURL=https://github.com/jackfahdin/ZzXsrv
DefaultDirName={autopf}\ZzXsrv
DefaultGroupName=ZzXsrv
; Per-user install by default; user may choose all-users (admin) in the dialog.
; Inno routes registry/shell writes to HKCU or HKLM automatically per mode.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#ZxOutDir}
OutputBaseFilename={#ZxOutName}
Compression=lzma2/ultra64
SolidCompression=yes
LicenseFile={#ZxLicenseFile}
WizardStyle=modern
UninstallDisplayIcon={app}\vcxsrv.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#ZxDistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\XLaunch"; Filename: "{app}\xlaunch.exe"
Name: "{group}\ZzXsrv (multiwindow)"; Filename: "{app}\vcxsrv.exe"; Parameters: "-multiwindow -clipboard"
Name: "{group}\Uninstall ZzXsrv"; Filename: "{uninstallexe}"
