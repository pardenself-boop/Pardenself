#define MyAppName "BOOM BAP TOOLBOXX"
#ifndef MyAppVersion
  #error MyAppVersion must be passed by BUILD_SETUP_WINDOWS.ps1
#endif
#ifndef InstallerBase
  #error InstallerBase must be passed by BUILD_SETUP_WINDOWS.ps1
#endif
#define MyAppExeName "BOOM_BAP_TOOLBOXX.exe"
[Setup]
AppId={{E59D55E5-8367-40E6-937A-A25CF41F3A8B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\Programs\BOOM BAP TOOLBOXX
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename={#InstallerBase}
Compression=lzma2
SolidCompression=yes
DiskSpanning=no
SetupLogging=yes
PrivilegesRequired=lowest
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}
CloseApplications=yes
[Files]
Source: "..\build\BOOM_BAP_TOOLBOXX\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
[Icons]
Name: "{group}\BOOM BAP TOOLBOXX"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\STREET SOUND CHECK (Audio + MIDI)"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--sound-check"
Name: "{autodesktop}\BOOM BAP TOOLBOXX"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch BOOM BAP TOOLBOXX"; Flags: nowait postinstall skipifsilent
