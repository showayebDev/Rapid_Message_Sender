# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/rapid_message_sender/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/rapid_message_sender/ui/assets', 'rapid_message_sender/ui/assets'),
    ],
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
    a.binaries,
    a.datas,
    [],
    name='RapidMessageSender',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/rapid_message_sender/ui/assets/app_icon.ico',
)
