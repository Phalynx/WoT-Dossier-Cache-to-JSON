@echo off
SET pythonexe=d:\Python27\python.exe
@%pythonexe% .\compile.py

@%pythonexe% compile_exe.py py2exe

pause