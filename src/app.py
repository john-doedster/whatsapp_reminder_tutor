import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
from contacts_manager import ContactsManager
from path_config import PATHS

def setup_paths():
    """Настраиваем правильные пути к файлам"""
    # Получаем путь к папке проекта (на уровень выше src)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Меняем рабочую директорию на корень проекта
    os.chdir(project_root)
    
    # Добавляем папку src в путь поиска модулей
    src_path = os.path.join(project_root, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


setup_paths()

class WhatsAppReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Reminder для Репетиторов")
        self.root.geometry("800x600")
        
        self.contacts_manager = ContactsManager()
        
        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка контактов
        self.contacts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.contacts_frame, text='Контакты')
        self.setup_contacts_tab()
        
        # Вкладка управления
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text='Управление')
        self.setup_control_tab()
        
        # Загружаем контакты при запуске
        self.load_contacts_list()

    def setup_contacts_tab(self):
        # Поля для ввода нового контакта
        ttk.Label(self.contacts_frame, text="Имя ученика:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.name_entry = ttk.Entry(self.contacts_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.contacts_frame, text="Номер телефона:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.phone_entry = ttk.Entry(self.contacts_frame, width=30)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Кнопки
        ttk.Button(self.contacts_frame, text="Добавить контакт", 
                  command=self.add_contact).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Список контактов
        ttk.Label(self.contacts_frame, text="Список контактов:").grid(row=3, column=0, sticky='w', padx=5)
        self.contacts_listbox = tk.Listbox(self.contacts_frame, height=15)
        self.contacts_listbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        # Кнопки управления списком
        ttk.Button(self.contacts_frame, text="Удалить выбранный", 
                  command=self.delete_contact).grid(row=5, column=0, pady=5)
        ttk.Button(self.contacts_frame, text="Редактировать", 
                  command=self.edit_contact).grid(row=5, column=1, pady=5)
        
        # Настройка расширения
        self.contacts_frame.grid_rowconfigure(4, weight=1)
        self.contacts_frame.grid_columnconfigure(1, weight=1)

    def setup_control_tab(self):
        # Кнопка запуска
        ttk.Button(self.control_frame, text="🚀 Запустить рассылку", 
                  command=self.start_reminders, style='Accent.TButton').pack(pady=20)
        
        # Кнопка календаря
        ttk.Button(self.control_frame, text="📅 Открыть Google Календарь", 
                  command=self.open_calendar).pack(pady=10)
        
        # Лог
        ttk.Label(self.control_frame, text="Лог выполнения:").pack(pady=(20, 5), anchor='w')
        self.log_text = scrolledtext.ScrolledText(self.control_frame, height=15)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
                
        # Стиль для акцентной кнопки
        style = ttk.Style()
        style.configure('Accent.TButton', foreground='white', background='#007acc')

    def add_contact(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not name or not phone:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        
        if self.contacts_manager.add_contact(name, phone):
            self.name_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.load_contacts_list()
            self.log(f"Добавлен контакт: {name}")
        else:
            messagebox.showerror("Ошибка", "Контакт с таким именем уже существует")

    def delete_contact(self):
        """Удаление выбранного контакта"""
        selected = self.contacts_listbox.curselection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите контакт для удаления")
            return
            
        contact_str = self.contacts_listbox.get(selected[0])
        name = contact_str.split(' - ')[0]
        
        if messagebox.askyesno("Подтверждение", 
                            f"Вы уверены, что хотите удалить контакт {name}?"):
            if self.contacts_manager.delete_contact(name):
                self.load_contacts_list()
                self.log(f"Удален контакт: {name}")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить контакт")

    def edit_contact(self):
        """Редактирование выбранного контакта"""
        selected = self.contacts_listbox.curselection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите контакт для редактирования")
            return
            
        # Получаем данные выбранного контакта
        contact_str = self.contacts_listbox.get(selected[0])
        current_name, current_phone = contact_str.split(' - ')
        
        # Создаем окно редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование контакта")
        edit_window.geometry("300x150")
        
        # Поля для редактирования
        ttk.Label(edit_window, text="Имя ученика:").pack(pady=(10, 0))
        name_entry = ttk.Entry(edit_window, width=30)
        name_entry.pack(pady=5)
        name_entry.insert(0, current_name)
        
        ttk.Label(edit_window, text="Номер телефона:").pack()
        phone_entry = ttk.Entry(edit_window, width=30)
        phone_entry.pack(pady=5)
        phone_entry.insert(0, current_phone)    

        def save_changes():
            new_name = name_entry.get().strip()
            new_phone = phone_entry.get().strip()
            
            if not new_name or not new_phone:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            # Удаляем старый контакт и добавляем новый
            if self.contacts_manager.delete_contact(current_name):
                if self.contacts_manager.add_contact(new_name, new_phone):
                    self.load_contacts_list()
                    self.log(f"Контакт изменен: {current_name} → {new_name}")
                    edit_window.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось сохранить изменения")
        
        ttk.Button(edit_window, text="Сохранить", 
                command=save_changes).pack(pady=10)     

    def load_contacts_list(self):
        """Загрузка списка контактов в Listbox"""
        self.contacts_listbox.delete(0, tk.END)
        contacts = self.contacts_manager.get_contacts()
        
        for name, phone in contacts.items():
            # Используем оригинальное имя (не в lower case)
            display_name = name.capitalize()  # Делаем первую букву заглавной
            self.contacts_listbox.insert(tk.END, f"{display_name} - {phone}")

    def start_reminders(self):
        self.log("Запуск проверки напоминаний...")
        
        try:
            # Проверяем наличие credentials.json
            if not os.path.exists(PATHS['credentials']):
                self.log("❌ Файл credentials.json не найден")
                self.log("Разместите его в папке проекта:")
                self.log(PATHS['project_root'])
                return
            
            # Проверяем наличие папки data и contacts.json
            if not os.path.exists(PATHS['contacts']):
                self.log("⚠️ Файл contacts.json не найден, создаем default...")
                # Создаем default contacts.json
                default_contacts = {
                    "ученики": {
                        "пример ученика": "79000000000",
                        "илья фомка": "79137459251"
                    }
                }
                os.makedirs(PATHS['data_dir'], exist_ok=True)
                with open(PATHS['contacts'], 'w', encoding='utf-8') as f:
                    json.dump(default_contacts, f, ensure_ascii=False, indent=2)
                self.log("✅ Создан файл contacts.json с примерами")
            
            # Временно меняем рабочую директорию на корень проекта
            original_dir = os.getcwd()
            os.chdir(PATHS['project_root'])
            
            # Перехватываем вывод
            import sys
            from io import StringIO
            
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            
            # Запускаем основной скрипт
            try:
                from whatsapp_reminder import main
                main()
            except Exception as e:
                self.log(f"❌ Ошибка в скрипте: {str(e)}")
                import traceback
                self.log(traceback.format_exc())
            
            # Возвращаем вывод и восстанавливаем директорию
            sys.stdout = old_stdout
            os.chdir(original_dir)
            
            output = mystdout.getvalue()
            
            # Выводим результат
            for line in output.split('\n'):
                if line.strip():
                    self.log(line)
                    
        except Exception as e:
            self.log(f"❌ Критическая ошибка: {str(e)}")

    def open_calendar(self):
        import webbrowser
        webbrowser.open("https://calendar.google.com")
        self.log("Открыт Google Календарь")

    def log(self, message):
        # Временно включаем редактирование
        self.log_text.config(state='normal')
        # Добавляем сообщение
        self.log_text.insert(tk.END, message + "\n")
        # Прокручиваем к концу
        self.log_text.see(tk.END)
        # Снова отключаем редактирование
        self.log_text.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppReminderApp(root)
    root.mainloop()