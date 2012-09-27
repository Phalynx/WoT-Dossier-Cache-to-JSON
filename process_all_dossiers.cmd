@echo off
SET pythonexe=d:\Python27\python.exe
for /f %%f in ('dir /b .\*.dat') do @%pythonexe% .\wotdc2j.py .\%%f -f
pause