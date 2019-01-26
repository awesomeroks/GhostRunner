import cx_Freeze
import os
os.environ['TCL_LIBRARY'] = r'C:\Program Files\Python35-32\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Program Files\Python35-32\tcl\tk8.6'

executables = [cx_Freeze.Executable("main.py")]
files = ['8bit.ttf', '8bitbgmusic.wav', 'abandoned.ttf', 'darkpix.ttf', 'electricintro.wav', 'exp2.png', 'exp3.png','exp4.png', 'exp5.png', 'exp6.png', 'expl1.png', 'gexpl.wav', 'hs.txt', 'map.txt', 'medal.png', 'pacdie.wav', 'pacdiefinal.wav', 'shoot.wav', 'settings.py']
cx_Freeze.setup(
    name="GhostRunner   ",
    options={"build_exe": {"packages":["pygame"],
                           "include_files":files}},
    executables = executables

    )