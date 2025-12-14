@echo off
call venv\Scripts\activate.bat
set PYTHONPATH=%CD%
%CD%\venv\Scripts\python.exe jobs\listen_all.py