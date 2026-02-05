# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['FD_yolo_model.py'],
    pathex=[],
    binaries=[],
    datas=[('models', 'models'), ('templates', 'templates'), ('static', 'static'), ('runtime_static', 'runtime_static'), ('capture_images_fire', 'capture_images_fire'), ('mode_config.json', '.'), ('yolov8n.pt', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FireDetectionApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app_icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FireDetectionApp',
)
