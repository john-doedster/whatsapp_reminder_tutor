import json
import os
from path_config import PATHS  # Убедитесь, что этот импорт есть

class ContactsManager:
    def __init__(self, filename=None):
        # Всегда используем путь из конфигурации к папке data
        self.filename = PATHS['contacts']
        self.contacts = self.load_contacts()
        print(f"Contacts file: {self.filename}")  # Для отладки

    def load_contacts(self):
        # Создаем папку data если не существует
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"Loaded {len(data.get('ученики', {}))} contacts")  # Отладка
                    return data.get('ученики', {})
            except Exception as e:
                print(f"Ошибка загрузки контактов: {e}")
                return {}
        else:
            # Создаем default файл в папке data
            default_data = {'ученики': {}}
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            print("Создан новый файл контактов в папке data")
            return {}

    def save_contacts(self):
        data = {'ученики': self.contacts}
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Контакты сохранены в: {self.filename}")

    def add_contact(self, name, phone):
        if name.lower() in self.contacts:
            return False
        self.contacts[name.lower()] = phone
        self.save_contacts()
        return True

    def delete_contact(self, name):
        """Удаляет контакт по имени"""
        clean_name = name.split(' - ')[0].lower().strip()
        if clean_name in self.contacts:
            del self.contacts[clean_name]
            self.save_contacts()
            return True
        return False

    def get_contacts(self):
        return self.contacts

    def get_phone(self, name):
        return self.contacts.get(name.lower())