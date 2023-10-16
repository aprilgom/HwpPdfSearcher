from cx_Freeze import setup, Executable
import sys
buildOptions = dict(packages = ["elasticsearch", "pdfminer"]
                    ,includes = ["PyQt5"]
                    ,include_files = ["folderlistdiag.ui","settingdiag.ui","window.ui"]
                    , excludes = [])  # 1

base = None
if sys.platform == "win32":
    base = "Win32GUI"
exe = [Executable("main.py",base=base)]  # 2

# 3
setup(
    name='hwppdfindexer',
    version = '0.1',
    author = "aprilgom@gmail.com",
    options = dict(build_exe = buildOptions),
    executables = exe
)