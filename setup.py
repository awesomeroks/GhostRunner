import cx_Freeze
import os
PYTHON_INSTALL_DIR = r'C:\Users\pveen\AppData\Local\Programs\Python\Python37'
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

executables = [cx_Freeze.Executable("GhostRunner.py")]
files = ['8bit.ttf', '8bitbgmusic.wav', 'abandoned.ttf', 'darkpix.ttf', 'electricintro.wav', 'exp2.png', 'exp3.png','exp4.png', 'exp5.png', 'exp6.png', 'expl1.png', 'gexpl.wav', 'hs.txt', 'map.txt', 'medal.png', 'pacdie.wav', 'pacdiefinal.wav', 'shoot.wav', 'settings.py',os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll')]

options = {
    'build_exe': {
        'include_files':files,
        "packages":["pygame", "json","random","pygame.gfxdraw","time"]
    },
}

cx_Freeze.setup(
    options = options,
    name="GhostRunner",
    executables = executables

    )