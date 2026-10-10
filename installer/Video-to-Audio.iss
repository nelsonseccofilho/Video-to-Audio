#define MyAppName "Video-to-Audio"
#define MyAppVersion "0.3.1"
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
VersionInfoVersion=0.3.1.0
VersionInfoDescription=Video to Audio Converter Installer
VersionInfoCompany={#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
CloseApplications=yes
RestartApplications=no
LanguageDetectionMethod=none
; Always start with English, even when upgrading an earlier Portuguese install.
UsePreviousLanguage=no
ShowLanguageDialog=yes

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"; LicenseFile: "..\LICENSE"
Name: "ptbr"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"; LicenseFile: "..\installer\LICENSE.pt-BR.txt"

[Messages]
; The language-selection dialog is shown before any new choice takes effect.
; Show bilingual guidance so its meaning stays clear while changing the list.
en.SelectLanguageTitle=Setup language / Idioma da instalação
ptbr.SelectLanguageTitle=Setup language / Idioma da instalação
en.SelectLanguageLabel=Select the installer language / Selecione o idioma do instalador:
ptbr.SelectLanguageLabel=Select the installer language / Selecione o idioma do instalador:

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
Source: "..\LICENSES\GPL-3.0-only.txt"; DestDir: "{app}\licenses"; Flags: ignoreversion
Source: "..\LICENSES\BSD-2-Clause-imageio-ffmpeg.txt"; DestDir: "{app}\licenses"; Flags: ignoreversion
Source: "..\docs\OPEN_SOURCE_DISTRIBUTION_POLICY.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\installer\LICENSE.pt-BR.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; DestName: "THIRD_PARTY_NOTICES.md"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent
