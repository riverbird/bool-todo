# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\project\\gitee\\shiqu-note\\assets\\', 'assets'), ('D:\\project\\gitee\\shiqu-note\\py310venv\\Lib\\site-packages\\PySide6', 'PySide6'), ('D:\\project\\gitee\\shiqu-note\\py310venv\\Lib\\site-packages\\shiboken6', 'shiboken6'), ('D:\\project\\gitee\\shiqu-note\\py310venv\\Lib\\site-packages\\requests\\', 'requests'), ('D:\\project\\gitee\\shiqu-note\\py310venv\\Lib\\site-packages\\certifi\\', 'certifi'), ('D:\\project\\gitee\\shiqu-note\\py310venv\\Lib\\site-packages\\charset_normalizer\\', 'charset_normalizer'), ('D:\\project\\gitee\\shiqu-note\\py310venv\\Lib\\site-packages\\idna\\', 'idna'), ('D:\\project\\gitee\\shiqu-note\\py310venv\\Lib\\site-packages\\urllib3\\', 'urllib3')],
    hiddenimports=['__future__', 'hmac', 'queue', 'http.cookies', 'importlib.resources'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='shiqu-note',
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
    icon=['D:\\project\\gitee\\shiqu-note\\assets\\icons\\shiqu-256.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='shiqu-note',
)
