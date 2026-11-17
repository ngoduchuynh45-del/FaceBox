import os

DESKTOP = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
EXE = r"D:\Project Antigravity IDE\Dự án FaceBox\FaceBox\dist\FaceBox\FaceBox.exe"

# Remove old bat if exists
bat = os.path.join(DESKTOP, "FaceBox.bat")
if os.path.exists(bat):
    os.remove(bat)
    print("Removed .bat")

# Remove bad .lnk from previous failed attempt
lnk = os.path.join(DESKTOP, "FaceBox.lnk")
if os.path.exists(lnk):
    os.remove(lnk)
    print("Removed bad .lnk")

# Create .vbs launcher (no console window, launches silently)
vbs_path = os.path.join(DESKTOP, "FaceBox.vbs")
vbs_lines = [
    'Set WshShell = WScript.CreateObject("WScript.Shell")',
    'exePath = "' + EXE + '"',
    'WshShell.Run Chr(34) & exePath & Chr(34), 0, False',
]
with open(vbs_path, "w", encoding="utf-8") as f:
    f.write("\r\n".join(vbs_lines) + "\r\n")

print(f"Created VBS launcher: {vbs_path}")
print(f"File exists: {os.path.exists(vbs_path)}")
print(f"File size: {os.path.getsize(vbs_path)} bytes")

