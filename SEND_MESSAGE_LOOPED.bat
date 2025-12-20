@echo off
:loop
call venv\Scripts\activate.bat
set PYTHONPATH=%CD%
%CD%\venv\Scripts\python.exe jobs\cron_send_message.py
timeout /t 40 /nobreak >nul
goto loop