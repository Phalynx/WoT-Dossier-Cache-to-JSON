@echo off
SET pythonexe=d:\Python27\python.exe
for /f %%f in ('dir /b .\dossiers\*.dat') do @%pythonexe% .\wotdc2j.py .\dossiers\%%f -f -r
pause