from py2exe.build_exe import py2exe
from distutils.core import setup
setup(windows=[{"script": "log_viewer.py"}], options={"py2exe":{"includes":["sip"]}})
