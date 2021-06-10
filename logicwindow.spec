# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

py_files = [
    'UI\\logicwindow.py',
    'UI\\startwindow.py',
    'UI\\logic_no_file.py',
    'UI\\logic_no_savepath.py',
    'UI\\no_savepath_reminder.py',
    'UI\\no_file_reminder.py',
    'UI\\src_rc.py',
    'BackendLogic.py',
]

add_files = [
    ('UI\\dase_ecnu.png', 'images'),
    ('UI\\company.png', 'images'),
    ('UI\\picture.png', 'images'),
    ('UI\\logo.ico', 'images'),
    ('seat_distribution\\NO_1_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_2_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_3_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_4_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_5_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_6_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_7_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_8_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_9_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_10_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_11_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_12_seat_distribution.npy','.\\seat_distribution'),
    ('seat_distribution\\NO_13_seat_distribution.npy','.\\seat_distribution')
]


a = Analysis(py_files,
             pathex=['D:\\Theater-seat-analysis-system'],
             binaries=[],
             datas=add_files,
             hiddenimports=['src_rc'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SAIC-SHCS-TSAS',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='D:\\Theater-seat-analysis-system\\UI\\logo.ico')
