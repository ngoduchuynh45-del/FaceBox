# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec file cho FaceBox Industrial Smart Locker.
Đóng gói theo phương án onedir, GUI không hiển thị console terminal,
tự động bao gồm models ONNX, schema database và icon Windows.
Tương thích Windows x64.
"""

import sys
import os
from pathlib import Path

block_cipher = None

# Xác định thư mục dự án an toàn qua SPECPATH của PyInstaller (tránh phụ thuộc vào cwd khi chạy lệnh)
if 'SPECPATH' in globals() and SPECPATH:
    PROJ_DIR = Path(SPECPATH).resolve()
else:
    PROJ_DIR = Path(__file__).parent.resolve() if '__file__' in globals() else Path.cwd().resolve()

# Danh sách dữ liệu kèm theo (source_path, target_folder)
datas = [
    (str(PROJ_DIR / 'models'), 'models'),
    (str(PROJ_DIR / 'database' / 'schema.sql'), 'database'),
    (str(PROJ_DIR / 'assets'), 'assets'),
]

# Các hidden imports để đảm bảo nạp động đầy đủ Qt, OpenCV, NumPy, SQLite và các module FaceBox
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'cv2',
    'numpy',
    'sqlite3',
    'PIL',
    'PIL.Image',
    # Các service và module nội bộ FaceBox
    'services.path_service',
    'services.camera_service',
    'services.face_recognition_service',
    'services.account_service',
    'database.db_manager',
    'ui.theme',
    'ui.app_controller',
    'ui.main_window',
    'ui.styles',
    'ui.widgets',
    'ui.components',
    'ui.dashboard_page',
    'ui.registration_page',
    'ui.recognition_page',
    'ui.accounts_page',
    'ui.admin.history_page',
    'ui.admin.locker_page',
    'ui.admin.login_page',
    'ui.admin.settings_page',
    'ui.kiosk.kiosk_shell',
    'ui.kiosk.welcome_page',
    'ui.kiosk.transaction_choice_page',
    'ui.kiosk.auth_choice_page',
    'ui.kiosk.phone_input_page',
    'ui.kiosk.face_scan_page',
    'ui.kiosk.send_item_page',
    'ui.kiosk.pickup_item_page',
    'ui.kiosk.complete_page',
]

a = Analysis(
    ['main.py'],
    pathex=[str(PROJ_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'notebook',
        'pytest',
        'unittest',
        'scipy',
        'pandas',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FaceBox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,                  # Không hiển thị cửa sổ console đen cho ứng dụng Kiosk
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,               # Biên dịch theo kiến trúc Windows x64 của môi trường
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJ_DIR / 'assets' / 'FaceBox.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='FaceBox',
)

