@echo off
call venv\Scripts\activate.bat
set PYTHONPATH=%CD%
%CD%\venv\Scripts\python.exe jobs\cron_send_message.py
pause