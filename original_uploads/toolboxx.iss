#define MyAppName "BOOM BAP TOOLBOXX"
#define MyAppVersion "0.50.0"
#define MyAppExeName "BOOM_BAP_TOOLBOXX.exe"
[Setup]
AppId={{E59D55E5-8367-40E6-937A-A25CF41F3A8B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\Programs\BOOM BAP TOOLBOXX
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename=BOOM_BAP_TOOLBOXX_Setup_050
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
WizardStyle=modern
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
