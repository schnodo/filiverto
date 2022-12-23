from cx_Freeze import setup, Executable

base = None

executables = [Executable("filiverto.pyw", base="Win32GUI", icon="ToDoList_2004.ico")]

packages = ["idna", "os", "sys", "csv", "tkinter", "urllib.parse", "re"]

include_files = ["ToDoList_2004.ico"]

options = {
    "build_exe": {
        "packages": packages,
    },
}

setup(
    name="filiverto",
    options={"build_exe": {"include_files": "ToDoList_2004.ico"}},
    version="0.9.0",
    description="File Link Verifier for AbstractSpoon's ToDoList",
    executables=executables,
)
