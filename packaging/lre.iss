#define MyAppName "Local Research"
#define MyAppVersion GetEnv("LRE_VERSION")
#define MyAppPublisher "Local Research contributors"

[Setup]
AppId={{6A76248B-3690-4B7A-91C9-2E9E1B54E8FA}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Local Research
DefaultGroupName=Local Research
OutputDir=..\dist
OutputBaseFilename=LocalResearch-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName=Local Research

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
Name: "deleteuserdata"; Description: "Also delete local chats, settings, and downloaded models on uninstall"; Flags: unchecked

[Files]
Source: "..\dist\LocalResearch\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Local Research"; Filename: "{app}\LocalResearch.exe"
Name: "{autodesktop}\Local Research"; Filename: "{app}\LocalResearch.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LocalResearch.exe"; Description: "Launch Local Research"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataPath, LocalAppDataPath: String;
begin
  if (CurUninstallStep = usPostUninstall) and WizardIsTaskSelected('deleteuserdata') then begin
    AppDataPath := ExpandConstant('{userappdata}\LocalResearch');
    LocalAppDataPath := ExpandConstant('{localappdata}\LocalResearch');
    DelTree(AppDataPath, True, True, True);
    DelTree(LocalAppDataPath, True, True, True);
  end;
end;
