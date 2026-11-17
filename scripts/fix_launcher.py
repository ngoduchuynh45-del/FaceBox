"""
Lấy Windows short path (8.3) và tạo FaceBox.vbs với đường dẫn an toàn.
Dùng ctypes để gọi GetShortPathNameW từ kernel32.
"""
import ctypes
import os
import sys

def get_short_path(long_path):
    """Lấy Windows 8.3 short path từ long path Unicode."""
    buf_size = ctypes.windll.kernel32.GetShortPathNameW(long_path, None, 0)
    if buf_size == 0:
        return None
    buf = ctypes.create_unicode_buffer(buf_size)
    ctypes.windll.kernel32.GetShortPathNameW(long_path, buf, buf_size)
    return buf.value

# Đường dẫn thực tế
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE_PATH = os.path.join(PROJECT_ROOT, "dist", "FaceBox", "FaceBox.exe")
WORK_DIR  = os.path.join(PROJECT_ROOT, "dist", "FaceBox")
DESKTOP   = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
VBS_PATH  = os.path.join(DESKTOP, "FaceBox.vbs")

print(f"[CHECK] EXE exists: {os.path.exists(EXE_PATH)}")
print(f"[CHECK] EXE path  : {EXE_PATH}")

if not os.path.exists(EXE_PATH):
    print("[ERROR] FaceBox.exe không tìm thấy! Hãy build lại bằng PyInstaller.")
    sys.exit(1)

# Lấy short path
short_exe  = get_short_path(EXE_PATH)
short_work = get_short_path(WORK_DIR)

print(f"[SHORT] EXE      : {short_exe}")
print(f"[SHORT] WORK_DIR : {short_work}")

if not short_exe:
    print("[ERROR] Không thể lấy short path. 8.3 filename có thể bị tắt trên hệ thống.")
    sys.exit(1)

# Viết VBS với short path - đảm bảo CRLF đúng (không double CR)
vbs_content = (
    'Set WshShell = WScript.CreateObject("WScript.Shell")\r\n'
    f'exePath = "{short_exe}"\r\n'
    f'workDir = "{short_work}"\r\n'
    '\r\n'
    'If Len(Dir(exePath)) = 0 Then\r\n'
    '    MsgBox "Khong tim thay FaceBox.exe!" & Chr(13) & Chr(10) & _\r\n'
    '           exePath, 16, "FaceBox - Loi khoi dong"\r\n'
    'Else\r\n'
    '    WshShell.CurrentDirectory = workDir\r\n'
    '    WshShell.Run Chr(34) & exePath & Chr(34), 0, False\r\n'
    'End If\r\n'
)

with open(VBS_PATH, "w", encoding="ascii", errors="replace", newline="") as f:
    f.write(vbs_content)

print(f"[OK] VBS created  : {VBS_PATH}")
print(f"[OK] File size    : {os.path.getsize(VBS_PATH)} bytes")
print()
print("--- VBS content ---")
print(vbs_content)

