; ─────────────────────────────────────────────────────────────────────────────
; FaceBox — Inno Setup Script
; Bộ cài đặt Windows chính thức (FaceBox_Setup.exe)
; Tương thích: Windows 10 / Windows 11 (64-bit)
; ─────────────────────────────────────────────────────────────────────────────

#define MyAppName "FaceBox"
#define MyAppVersion "1.3.1"
#define MyAppPublisher "FaceBox Team"
#define MyAppExeName "FaceBox.exe"
#define MyAppAssocName MyAppName + " Application"
#define SourceDir "..\dist\FaceBox"

[Setup]
; AppId duy nhất định danh FaceBox (dùng để nhận diện bản nâng cấp phiên bản)
AppId={{8B19C92D-6F14-4A2D-A482-A7E5E32890C1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Quyền cài đặt: Cho phép cài cho từng người dùng (không cần Admin) hoặc cài cho cả máy
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Thư mục xuất file cài đặt
OutputDir=..\dist
OutputBaseFilename=FaceBox_v{#MyAppVersion}_Setup_x64

; Tích hợp Icon chính thức
SetupIconFile=..\assets\FaceBox.ico
UninstallDisplayIcon={app}\_internal\assets\FaceBox.ico

; Thuật toán nén tối ưu
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Yêu cầu Windows 64-bit
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Sao chép toàn bộ thư mục đã đóng gói dist\FaceBox
; QUAN TRỌNG: Loại trừ data\facebox.db để không bao giờ ghi đè database cá nhân khi cập nhật!
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "data\facebox.db,logs\*.log"

[Icons]
; Shortcut trong Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\_internal\assets\FaceBox.ico"
; Shortcut Gỡ cài đặt trong Start Menu
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Shortcut trên Desktop (tùy chọn)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\_internal\assets\FaceBox.ico"; Tasks: desktopicon

[Run]
; Tùy chọn khởi chạy ứng dụng sau khi cài đặt hoàn tất
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Dọn dẹp logs khi gỡ cài đặt
; TUYỆT ĐỐI KHÔNG XÓA file database data\facebox.db hoặc %LOCALAPPDATA%\FaceBox để bảo vệ dữ liệu người dùng
Type: files; Name: "{app}\logs\*.log"
Type: dirifempty; Name: "{app}\logs"
