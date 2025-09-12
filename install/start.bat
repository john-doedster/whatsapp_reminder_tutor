@echo off
chcp 65001 > nul
echo Запуск WhatsApp Reminder...
echo ==============================
cd /d "%~dp0"
python src\app.py
pause