#! pyinstaller --onefile
from PyInstaller.utils.hooks import collect_data_files

import gooey
gooey_root = os.path.dirname(gooey.__file__)
gooey_languages = Tree(os.path.join(gooey_root, 'languages'), prefix = 'gooey/languages')
gooey_images = Tree(os.path.join(gooey_root, 'images'), prefix = 'gooey/images')

block_cipher = None


a = Analysis(['bluerov2_usbl/gui.py'],
             pathex=['/home/dan/Documents/Cerulean-Companion'],
             hookspath=[],
             runtime_hooks=[],
             datas=collect_data_files('bluerov2_usbl'),
             )
pyz = PYZ(a.pure)
options = [('u', None, 'OPTION')]

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          options,
          gooey_languages, # Add them in to collected files
          gooey_images, # Same here.
          name='CeruleanCompanion',
          debug=False,
          strip=False,
          upx=True,
          console=False
          )
