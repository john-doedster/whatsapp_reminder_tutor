import json
import re
import datetime
import time
from datetime import timezone
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path

# ===== НАСТРОЙКИ =====
REMIND_BEFORE_HOURS = 24  # За сколько часов напоминать
CALENDAR_ID = 'primary'   # ID вашего календаря (обычно 'primary' для основного)
WHATSPP_SCAN_TIMEOUT = 60 # Секунд на сканирование QR-кода WhatsApp
# =====================

# Функция загрузки контактов
def load_contacts():
    try:
        with open('contacts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('ученики', {})
    except FileNotFoundError:
        print("Файл contacts.json не найден. Создайте файл с контактами.")
        return {}
    except json.JSONDecodeError:
        print("Ошибка в формате contacts.json. Проверьте файл.")
        return {}

# Функция для авторизации в Google Calendar API
def get_calendar_service():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

# Функция для получения событий из календаря
def get_upcoming_events(service, hours_ahead=48):
    now = datetime.datetime.now(timezone.utc).isoformat()
    end_time = (datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=hours_ahead)).isoformat()

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now,
        timeMax=end_time,
        maxResults=20,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    return events_result.get('items', [])

# Функция для отправки сообщения в WhatsApp
def send_whatsapp_message(phone_number, message):
    # Форматируем номер телефона (убираем всё, кроме цифр, и добавляем код страны)
    phone_number = ''.join(filter(str.isdigit, phone_number))
    if phone_number.startswith('0'):
        phone_number = '7' + phone_number[1:]  # Для российских номеров
    
    chat_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"

    # Настраиваем браузер
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=C:/WhatsAppBot/User_Data")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-gpu")
    
    driver = None
    
    try:
        from selenium.webdriver.chrome.service import Service
        service = Service(executable_path='./chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get("https://web.whatsapp.com")
        print(f"Пожалуйста, отсканируйте QR-код WhatsApp Web в течение {WHATSPP_SCAN_TIMEOUT} секунд...")
        
        WebDriverWait(driver, WHATSPP_SCAN_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "side"))
        )
        print("Успешный вход в WhatsApp Web!")

        # Переходим в нужный чат
        driver.get(chat_url)
        # Ждем загрузки поля ввода сообщения
        inp_xpath = '//div[@contenteditable="true"][@data-tab="10"]'
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, inp_xpath))
        )
        # Даем время на загрузку страницы
        time.sleep(2)
        # Нажимаем Enter для отправки сообщения
        webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
        print(f"Сообщение отправлено для {phone_number}")
        time.sleep(3)  # Ждем отправки

    except Exception as e:
        print(f"Ошибка при отправке сообщения {phone_number}: {str(e)}")
    finally:
        if driver is not None:
            driver.quit()

# Главная функция
def main():
    print("Запуск скрипта напоминаний...")
    
    # Загружаем контакты при запуске
    contacts = load_contacts()
    if not contacts:
        print("Не удалось загрузить контакты. Проверьте файл contacts.json")
        return
    
    # Получаем события из календаря
    service = get_calendar_service()
    events = get_upcoming_events(service, hours_ahead=REMIND_BEFORE_HOURS+2)

    now = datetime.datetime.now(timezone.utc)
    reminder_time = now + datetime.timedelta(hours=REMIND_BEFORE_HOURS)
    
    processed_numbers = set()  # Для избежания дублирования

    for event in events:
        start_str = event['start'].get('dateTime', event['start'].get('date'))
        
        # Преобразуем строку в aware datetime
        if 'Z' in start_str:
            start_time = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
        else:
            start_time = datetime.datetime.fromisoformat(start_str)
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)

        # Проверяем, нужно ли отправить напоминание на это событие СЕЙЧАС
        if abs((start_time - reminder_time).total_seconds()) < 3600:
            event_summary = event.get('summary', '').strip()
            
            # Имя ученика - это просто заголовок события
            student_name = event_summary
            
            if student_name:
                # Ищем номер в базе контактов
                student_key = student_name.lower().strip()
                phone_number = contacts.get(student_key)
                
                if phone_number:
                    # Проверяем дублирование
                    if phone_number in processed_numbers:
                        print(f"Пропускаем дубликат для номера {phone_number}")
                        continue
                    
                    processed_numbers.add(phone_number)
                    
                    # Формируем сообщение
                    message = f"Привет! Напоминаю, что {start_time.strftime('%d.%m')} в {start_time.strftime('%H:%M')} у нас занятие. Жду вас! 🎓"
                    message_encoded = quote(message)
                    
                    print(f"Найдено событие для: {student_name}. Телефон: {phone_number}")
                    send_whatsapp_message(phone_number, message_encoded)
                else:
                    print(f"Для ученика '{student_name}' не найден номер в контактах")
            else:
                print(f"Пустое название события")

    print("Проверка завершена.")

if __name__ == '__main__':
    main()