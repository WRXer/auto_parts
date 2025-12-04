import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')    #Устанавливаем настройки Django

app = Celery('config')   #Создаем экземпляр Celery. Имя 'config' должно совпадать с именем папки, содержащей settings.py

app.config_from_object('django.conf:settings', namespace='CELERY')    #Загружаем конфигурацию из Django-настроек. Все настройки Celery должны начинаться с префикса 'CELERY_'

app.autodiscover_tasks()    #Автоматически находим задачи в приложениях Django. Celery будет искать файл tasks.py в каждом приложении из INSTALLED_APPS


@app.task(bind=True)
def debug_task(self):   #Опционально: тестовая задача для проверки
    print(f'Request: {self.request!r}')