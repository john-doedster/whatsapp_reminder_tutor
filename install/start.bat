@echo off
chcp 65001 > nul
echo ========================================
echo    WhatsApp Reminder Bot Запускается
echo ========================================
cd /d "C:\Users\lalip\Desktop\ScriptWhatsApp"
python whatsapp_reminder.py
echo.
echo ========================================
echo    Скрипт завершил работу
echo    Нажмите любую клавишу для выхода...
echo ========================================
pause > nul