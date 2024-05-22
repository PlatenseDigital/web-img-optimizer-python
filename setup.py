from cx_Freeze import setup, Executable

target = Executable(
    script="wio.py",
    base="Win32GUI",
    icon="icon.ico"
    )

build_exe_options = {
    "packages": ["os", "tkinter", "PIL", "zipfile", "datetime", "re", "math", "tkinterdnd2"], 
    "include_files": ['favicon.png', 'logo.png', 'icon.ico']
}

setup(
    name="Web image optimizer",
    version="1.1.0",
    description="An webp converter by Platense Digital",
    author = 'Guido Schmidt',
    executables=[target],
    options = {'build_exe': build_exe_options}
)
