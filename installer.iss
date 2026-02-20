; Kreatív Diktáló - Inno Setup Installer Script
; ====================================================================
;
; Ez a script egy professzionális Windows telepítőt készít
; Használat: Töltsd le az Inno Setup-ot (https://jrsoftware.org/isinfo.php)
;            majd fordítsd le ezt a fájlt
;
; ====================================================================

#define MyAppName "Kreatív Diktáló"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Kreatív Diktáló Team"
#define MyAppURL "https://github.com/yourusername/kreativ-diktalo"
#define MyAppExeName "KreativDiktalo.exe"

[Setup]
; Alapvető beállítások
AppId={{A7B8C9D0-E1F2-3456-7890-ABCDEF123456}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=dist\installer
OutputBaseFilename=KreativDiktalo_Setup_{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Admin jogok kérése (FONTOS a hotkey működéséhez!)
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Windows verzió követelmények
MinVersion=10.0.17763
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "hungarian"; MessagesFile: "compiler:Languages\Hungarian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Az összes fájl a dist\KreativDiktalo mappából
Source: "dist\KreativDiktalo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Config fájl (user-editable, ne írja felül újratelepítéskor)
Source: "config.yaml"; DestDir: "{app}"; Flags: onlyifdoesntexist uninsneveruninstall

; Dokumentáció
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "ASSEMBLYAI_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "GROQ_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut (Admin jogokkal fut!)
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Parameters: ""; IconFilename: "{app}\{#MyAppExeName}"; Flags: runasadmin

; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon; Flags: runasadmin

; Quick Launch shortcut
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; Flags: runasadmin

[Run]
; Telepítés után kérdezze meg, hogy elindítsa-e
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent runascurrentuser

[Code]
// Admin jogok ellenőrzése telepítés előtt
function InitializeSetup(): Boolean;
begin
  Result := True;

  // Ellenőrizd hogy admin jogokkal fut-e
  if not IsAdminInstallMode then
  begin
    MsgBox('Ez a telepítő admin jogokat igényel!' + #13#10 +
           'Kérlek futtasd újra "Futtatás rendszergazdaként" opcióval.',
           mbError, MB_OK);
    Result := False;
  end;
end;

// Telepítés befejezése után
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('Telepítés sikeres!' + #13#10 + #13#10 +
           'FONTOS: Az alkalmazás ADMIN JOGOKKAL fut automatikusan.' + #13#10 +
           'Ez szükséges a globális F8 hotkey működéséhez.',
           mbInformation, MB_OK);
  end;
end;
