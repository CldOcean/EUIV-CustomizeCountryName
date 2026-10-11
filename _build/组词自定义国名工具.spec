# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('F:/WorkPlace/.ProjectsDateless/自定义国名/tools/组词自定义国名工具 - github/web/static', 'web/static'), ('F:/WorkPlace/.ProjectsDateless/自定义国名/tools/组词自定义国名工具 - github/区域-tag-国名对照表.md', '.')]
binaries = []
hiddenimports = ['gen_namebuilder', 'region_names', 'eu4_loc_codec']
tmp_ret = collect_all('webview')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pythonnet')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('clr_loader')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pypinyin')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['F:/WorkPlace/.ProjectsDateless/自定义国名/tools/组词自定义国名工具 - github/_build/entry.py'],
    pathex=['F:/WorkPlace/.ProjectsDateless/自定义国名/tools/组词自定义国名工具 - github', 'F:/WorkPlace/.ProjectsDateless/自定义国名/tools'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='组词自定义国名工具',
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
    icon=['F:/WorkPlace/.ProjectsDateless/自定义国名/tools/组词自定义国名工具 - github/_build/app.ico'],
)
