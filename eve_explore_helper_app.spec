# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_dir = Path(globals().get("SPECPATH", ".")).resolve()

datas = [
    (str(project_dir / "name_list.json"), "."),
    (str(project_dir / "starmap_processed.json"), "."),
    (str(project_dir / "constellations.json"), "."),
]

block_cipher = None

a = Analysis(
    ['eve_explore_helper_app.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EVE-Explore-Helper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
