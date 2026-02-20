# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec fájl - Kreatív Diktáló Windows .exe készítéséhez
"""

block_cipher = None

# Adatfájlok (config, assets, docs)
added_files = [
    ('config.template.yaml', '.'),  # Template config (placeholder API keys)
    ('SETUP_FIRST.md', '.'),        # FONTOS: Első indítás útmutató!
    ('README.md', '.'),              # Dokumentáció
    ('GROQ_SETUP.md', '.'),         # API setup útmutató
    ('ASSEMBLYAI_SETUP.md', '.'),   # API setup útmutató
    ('assets/icon.ico', 'assets'),
    ('assets/icon.png', 'assets'),
]

# Hidden imports (olyan modulok amik dinamikusan importálódnak)
hidden_imports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'sounddevice',
    'soundfile',
    'numpy',
    'scipy',
    'keyboard',
    'pynput',
    'pyautogui',
    'pyperclip',
    'groq',
    'assemblyai',
    'ollama',
    'yaml',
    'dotenv',
]

a = Analysis(
    ['src/gui_main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # UI libraries (nem használjuk)
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'tkinter',
        '_tkinter',

        # Helyi Whisper (nem kell, Groq API-t használunk!)
        'torch',
        'torchaudio',
        'torchvision',
        'faster_whisper',

        # Teszt/Dev tools
        'pytest',
        'black',
        'setuptools',
    ],
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
    name='KreativDiktalo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI app - ne mutasson konzolt
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    uac_admin=True,  # FONTOS: Admin jogok kérése (hotkey-hez kell!)
    uac_uiaccess=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KreativDiktalo',
)
