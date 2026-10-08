@echo off
cd /d "%~dp0"
set PYTHON_EXE=
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
if not defined PYTHON_EXE set PYTHON_EXE=python
"%PYTHON_EXE%" main.py
