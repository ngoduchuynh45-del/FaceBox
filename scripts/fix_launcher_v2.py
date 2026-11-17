"""
Tạo FaceBox.vbs dùng cmd /c start với đường dẫn Unicode.
WshShell.Run cmd là ASCII-safe; cmd.exe hỗ trợ Unicode path qua %windir%\system32\cmd.exe.
"""
import ctypes
import os
import sys

DESKTOP  = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
VBS_PATH = os.path.join(DESKTOP, "FaceBox.vbs")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE_PATH = os.path.join(PROJECT_ROOT, "dist", "FaceBox", "FaceBox.exe")
WORK_DIR  = os.path.join(PROJECT_ROOT, "dist", "FaceBox")

print(f"[CHECK] EXE exists: {os.path.exists(EXE_PATH)}")
print(f"[CHECK] EXE        : {EXE_PATH}")
print(f"[CHECK] WORK_DIR   : {WORK_DIR}")

if not os.path.exists(EXE_PATH):
    print("[ERROR] FaceBox.exe khong tim thay!")
    sys.exit(1)

# Escape backslash cho VBS string
vbs_exe  = EXE_PATH.replace("\\", "\\\\")
vbs_work = WORK_DIR.replace("\\", "\\\\")

# VBS dùng Shell.Open (ShellExecute) thay WshShell.Run
# Shell.Open hoạt động tốt với Unicode path hơn WshShell.Run
vbs_lines = [
    'Dim objShell',
    'Set objShell = CreateObject("Shell.Application")',
    '',
    'Dim exePath',
    f'exePath = "{EXE_PATH}"',
    '',
    'Dim fso',
    'Set fso = CreateObject("Scripting.FileSystemObject")',
    '',
    'If Not fso.FileExists(exePath) Then',
    '    MsgBox "Khong tim thay FaceBox.exe!" & Chr(13) & Chr(10) & exePath, 16, "FaceBox - Loi"',
    'Else',
    f'    objShell.ShellExecute exePath, "", "{WORK_DIR}", "open", 1',
    'End If',
    '',
    'Set fso = Nothing',
    'Set objShell = Nothing',
]

vbs_content = "\r\n".join(vbs_lines) + "\r\n"

# Ghi file với encoding cp1252 (Windows-1252) để tránh BOM và Unicode issues
with open(VBS_PATH, "w", encoding="cp1252", errors="replace", newline="\r\n") as f:
    f.write(vbs_content)

print(f"[OK] VBS saved: {VBS_PATH}")
print(f"[OK] Size: {os.path.getsize(VBS_PATH)} bytes")
print()

# Hiển thị nội dung thực tế
with open(VBS_PATH, "r", encoding="cp1252") as f:
    content = f.read()
print("--- VBS content (actual) ---")
print(content)

