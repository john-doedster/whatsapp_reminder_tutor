@echo off
chcp 65001 > nul
title Установка WhatsApp Reminder для Репетиторов

echo ====================================================
echo    WhatsApp Reminder - Установка и настройка
echo ====================================================
echo.

REM Проверяем, установлен ли Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не установлен или не добавлен в PATH!
    echo.
    echo 1. Скачайте Python с официального сайта:
    echo    https://www.python.org/downloads/
    echo.
    echo 2. Во время установки ОБЯЗАТЕЛЬНО отметьте:
    echo    [X] Add Python to PATH (Добавить Python в PATH)
    echo.
    echo 3. Перезапустите install.bat после установки Python
    echo.
    pause
    exit /b 1
)

echo ✓ Python обнаружен
echo.

REM Проверяем версию Python
python -c "import sys; print('Версия Python:', sys.version)"
echo.

REM Устанавливаем необходимые библиотеки
echo Устанавливаем необходимые библиотеки...
echo.

pip install selenium google-api-python-client google-auth-httplib2 google-auth-oauthlib requests >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки библиотек
    echo Попробуйте запустить от имени администратора
    pause
    exit /b 1
)

echo ✓ Библиотеки успешно установлены
echo.

REM Создаем папки для данных
if not exist "data" mkdir "data"
if not exist "C:\WhatsAppBot\User_Data" (
    mkdir "C:\WhatsAppBot\User_Data" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ⚠️ Не удалось создать папку C:\WhatsAppBot\User_Data
        echo Создайте ее вручную или запустите от имени администратора
    )
)

echo ✓ Папки для данных созданы
echo.

REM Проверяем наличие credentials.json
if not exist "credentials.json" (
    echo ⚠️ Файл credentials.json не найден!
    echo.
    echo Для работы программы необходимо:
    echo 1. Получить credentials.json из Google Cloud Console
    echo 2. Положить файл в эту папку: %CD%
    echo.
    echo Инструкция в файле INSTRUCTION.html
    echo.
)

REM Проверяем наличие chromedriver.exe
if not exist "chromedriver.exe" (
    echo ⚠️ ChromeDriver не найден. Пытаемся скачать...
    python -c "
import requests
import zipfile
import io
import os
import subprocess

try:
    # Пытаемся определить версию Chrome
    result = subprocess.run(['reg', 'query', 'HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon', '/v', 'version'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        version = result.stdout.split()[-1].rsplit('.', 1)[0]
        url = f'https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chromedriver-win64.zip'
        print(f'Скачиваем ChromeDriver для версии {version}...')
        
        response = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            zip_file.extractall()
        
        os.rename('chromedriver-win64\chromedriver.exe', 'chromedriver.exe')
        print('✓ ChromeDriver успешно установлен')
    else:
        print('Не удалось определить версию Chrome')
except Exception as e:
    print(f'Ошибка: {e}')
    print('Скачайте ChromeDriver вручную с:')
    print('https://googlechromelabs.github.io/chrome-for-testing/')
"
    echo.
)

REM Создаем стандартный contacts.json если нет
if not exist "data\contacts.json" (
    echo Создаем файл контактов...
    echo {
    echo   "ученики": {
    echo     "пример ученика": "79000000000",
    echo     "илья": "7XXXXXXXXXX"
    echo   }
    echo } > data\contacts.json
    echo ✓ Создан файл data\contacts.json
    echo.
)

REM Создаем start.bat если нет
if not exist "start.bat" (
    echo Создаем файл запуска...
    echo @echo off > start.bat
    echo chcp 65001 ^> nul >> start.bat
    echo echo Запуск WhatsApp Reminder... >> start.bat
    echo echo ============================== >> start.bat
    echo python src\app.py >> start.bat
    echo pause >> start.bat
    echo ✓ Создан файл start.bat
    echo.
)

echo ====================================================
echo    Установка завершена успешно! 🎉
echo.
echo    Что делать дальше:
echo.
if not exist "credentials.json" (
    echo    1. Получите credentials.json (см. INSTRUCTION.html)
)
echo    2. Запустите start.bat для начала работы
echo    3. Добавьте учеников во вкладке "Контакты"
echo    4. Настройте занятия в Google Календаре
echo    5. Запускайте рассылку кнопкой "Запустить рассылку"
echo.
echo    Папка с программой: %CD%
echo ====================================================
echo.
pause