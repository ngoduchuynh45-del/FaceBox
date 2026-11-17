# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec file cho FaceBox Industrial Smart Locker.
Đóng gói theo phương án onedir, GUI không hiển thị console terminal,
tự động bao gồm models ONNX, schema database và icon Windows.
"""

import sys
import os
from pathlib import Path

block_cipher = None

PROJ_DIR = Path.cwd().resolve()

# Danh sách dữ liệu kèm theo (source_path, target_folder)
datas = [
    (str(PROJ_DIR / 'models'), 'models'),
    (str(PROJ_DIR / 'database' / 'schema.sql'), 'database'),
    (str(PROJ_DIR / 'assets'), 'assets'),
]

# Các hidden imports để tránh thiếu sót khi nạp động
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'cv2',
    'numpy',
    'sqlite3',
    'PIL',
    'PIL.Image',
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
    excludes=['tkinter', 'matplotlib', 'notebook', 'pytest'],
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
    console=False,                  # Không hiển thị cửa sổ console đen
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
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

