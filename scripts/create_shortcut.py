"""
Script tạo Desktop shortcut cho FaceBox.
Dùng thư viện winshell / pythoncom với pywin32.
Fallback: tạo file .bat nếu không có pywin32.
"""
import os
import sys

DESKTOP = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(PROJECT_ROOT, "dist", "FaceBox", "FaceBox.exe")
WORK_DIR = os.path.join(PROJECT_ROOT, "dist", "FaceBox")
ICO = os.path.join(PROJECT_ROOT, "dist", "FaceBox", "_internal", "assets", "FaceBox.ico")
SHORTCUT = os.path.join(DESKTOP, "FaceBox.lnk")

print(f"EXE     : {EXE}")
print(f"WORK DIR: {WORK_DIR}")
print(f"ICO     : {ICO}")
print(f"DESKTOP : {DESKTOP}")

try:
    import win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    sc = shell.CreateShortcut(SHORTCUT)
    sc.TargetPath = EXE
    sc.WorkingDirectory = WORK_DIR
    sc.IconLocation = f"{ICO},0"
    sc.Description = "FaceBox - He Thong Tu Thong Minh"
    sc.Save()
    if os.path.exists(SHORTCUT):
        print(f"SUCCESS: Shortcut created at {SHORTCUT}")
    else:
        print("ERROR: Shortcut not created")
except ImportError:
    print("pywin32 not available, creating .bat launcher instead")
    bat_path = os.path.join(DESKTOP, "FaceBox.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(f'@echo off\r\nstart "" "{EXE}"\r\n')
    print(f"Created .bat launcher at: {bat_path}")
except Exception as e:
    print(f"Error: {e}")
    # Fallback to .bat
    bat_path = os.path.join(DESKTOP, "FaceBox.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(f'@echo off\r\nstart "" "{EXE}"\r\n')
    print(f"Created fallback .bat launcher at: {bat_path}")

