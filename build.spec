#! pyinstaller

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from PyInstaller.building.build_main import *

from PyInstaller.utils.hooks import collect_data_files

import gooey

gooey_root = os.path.dirname(gooey.__file__)
gooey_languages = Tree(os.path.join(gooey_root, 'languages'), prefix='gooey/languages')
gooey_images = Tree(os.path.join(gooey_root, 'images'), prefix='gooey/images')

block_cipher = None

for filename, exename, excludes in [
    # when building the CLI, exclude wx since it is huge
    ('bluerov2_usbl/cli.py', 'cerulean-companion', ['wx']),
    ('bluerov2_usbl/gui.py', 'cerulean-companion-gui', []),
]:
    a = Analysis(
        [filename],
        datas=collect_data_files('bluerov2_usbl'),
        excludes=excludes
    )
    pyz = PYZ(a.pure)
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              gooey_languages,
              gooey_images,
              name=exename,
              debug=False,
              strip=False,
              upx=True,
              console=False,
              )
