"""
Ghi FaceBox.vbs vao ca hai Desktop (local va OneDrive).
Su dung encoding ANSI (cp1252) va CRLF dung chuan VBScript.
"""
import os
import sys

VBS_CONTENT = (
    'Dim objShell\r\n'
    'Set objShell = CreateObject("Shell.Application")\r\n'
    '\r\n'
    'Dim fso\r\n'
    'Set fso = CreateObject("Scripting.FileSystemObject")\r\n'
    '\r\n'
    'Dim exePath\r\n'
    'exePath = "C:\\FaceBoxApp\\FaceBox.exe"\r\n'
    '\r\n'
    'If Not fso.FileExists(exePath) Then\r\n'
    '    MsgBox "Khong tim thay FaceBox.exe!" & Chr(13) & Chr(10) & exePath, 16, "FaceBox - Loi khoi dong"\r\n'
    'Else\r\n'
    '    objShell.ShellExecute exePath, "", "C:\\FaceBoxApp", "open", 1\r\n'
    'End If\r\n'
    '\r\n'
    'Set fso = Nothing\r\n'
    'Set objShell = Nothing\r\n'
)

# Danh sach Desktop candidates
desktops = [
    r'C:\Users\ADMIN\Desktop',
    os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
    os.path.join(os.environ.get('USERPROFILE', ''), 'OneDrive', 'Desktop'),
]
# Lay real Desktop tu Shell API
try:
    import ctypes.wintypes
    CSIDL_DESKTOP = 0
    buf = ctypes.create_unicode_buffer(260)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, 0, buf)
    real_desktop = buf.value
    if real_desktop and real_desktop not in desktops:
        desktops.insert(0, real_desktop)
    print(f"[SHELL] Real Desktop: {real_desktop}")
except Exception as e:
    print(f"[WARN] SHGetFolderPath failed: {e}")

written = []
for d in desktops:
    if os.path.isdir(d):
        vbs_path = os.path.join(d, 'FaceBox.vbs')
        try:
            with open(vbs_path, 'wb') as f:
                f.write(VBS_CONTENT.encode('ascii'))
            print(f"[OK] Written: {vbs_path} ({os.path.getsize(vbs_path)} bytes)")
            written.append(vbs_path)
        except Exception as e:
            print(f"[ERR] {d}: {e}")
    else:
        print(f"[SKIP] Not a dir: {d}")

print()
print(f"Total written: {len(written)}")
print()
print("--- VBS content ---")
print(VBS_CONTENT)

