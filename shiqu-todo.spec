# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\flet\\', 'flet'), ('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\beartype', 'beartype'), ('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\watchdog\\', 'watchdog'), ('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\websocket\\', 'websocket'), ('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\urllib3', 'urllib3'), ('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\repath.py', 'repath'), ('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\requests\\', 'requests'), ('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\charset_normalizer\\', 'charset_normalizer'), ('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\idna\\', 'idna'), ('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\certifi\\', 'certifi'), ('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\six.py', 'six'), ('D:\\project\\gitee\\shiqu-todo\\py310venv\\Lib\\site-packages\\oauthlib\\', 'oauthlib'), ('D:\\project\\gitee\\shiqu-todo\\assets\\', 'assets')],
    hiddenimports=['difflib', '__future__', 'queue', 'uuid', 'hmac', 'http.cookies', 'webbrowser', 'multiprocessing', 'unittest', 'importlib.resources'],
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
    name='shiqu-todo',
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
    icon='D:\\project\\gitee\\shiqu-todo\\assets\\icons\\shiqu-255.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='shiqu-todo',
)
