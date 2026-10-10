#define MyAppName "Video-to-Audio"
#define MyAppVersion "0.2.0"
#define MyAppExeName "Video-to-Audio.exe"
#define MyAppPublisher "Video-to-Audio Contributors"
#define MyAppURL "https://github.com/nelsonseccofilho/Video-to-Audio"

[Setup]
; Keep AppId stable across upgrades; do not regenerate it for new releases.
AppId={{0FCE6A17-0E2D-4AD2-85C0-609C2E9DE941}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
MinVersion=10.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\icons\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=..\dist\installer
OutputBaseFilename={#MyAppName}-Setup-{#MyAppVersion}
VersionInfoVersion=0.2.0.0
VersionInfoDescription=Video to Audio Converter Installer
VersionInfoCompany={#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
LicenseFile=..\LICENSE
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "ptbr"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[CustomMessages]
en.DesktopShortcut=Create a desktop shortcut
ptbr.DesktopShortcut=Criar um atalho na área de trabalho
en.AdditionalShortcuts=Additional shortcuts:
ptbr.AdditionalShortcuts=Atalhos adicionais:
en.LaunchApp=Launch Video-to-Audio
ptbr.LaunchApp=Executar Video-to-Audio

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopShortcut}"; GroupDescription: "{cm:AdditionalShortcuts}"; Flags: unchecked

[Files]
Source: "..\dist\Video-to-Audio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; DestName: "THIRD_PARTY_NOTICES.md"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent
