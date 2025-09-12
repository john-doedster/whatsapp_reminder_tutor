# path_config.py
import os
import sys

def configure_paths():
    """Настройка путей для приложения"""
    if getattr(sys, 'frozen', False):
        project_root = os.path.dirname(sys.executable)
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    paths = {
        'project_root': project_root,
        'credentials': os.path.join(project_root, 'credentials.json'),
        'token': os.path.join(project_root, 'token.json'),
        'contacts': os.path.join(project_root, 'data', 'contacts.json'),  # ← Важно!
        'chromedriver': os.path.join(project_root, 'chromedriver.exe'),
        'data_dir': os.path.join(project_root, 'data')
    }
    
    # Создаем папки если их нет
    os.makedirs(paths['data_dir'], exist_ok=True)
    
    return paths

PATHS = configure_paths()