from celery import shared_task
from spare_parts.management.fetch_prepare_donors import fetch_and_prepare_donors
from spare_parts.management.fetch_prepare_parts import fetch_and_prepare_parts
from spare_parts.management.import_to_db import import_donors_to_db, import_parts_to_db


class MockStdout:
    """
    Заглушка для stdout
    """
    def write(self, message, style_func=None):
        print(message)

    def terminal(self):
        return None

mock_stdout = MockStdout()


@shared_task(bind=True)
def update_catalog_task(self):
    """
    Основная задача Celery для запуска полного цикла обновления каталога в фоне.
    """
    try:
        from spare_parts.category_mapping import TRANSMISSION_MAP, CATEGORY_SLUG_MAP, CATEGORY_MAPPING, \
            GENERATION_MODELS
        from spare_parts.models import (
            CarMake, CarModel, CarGeneration, PartSubCategory, Part,
            DonorVehicle, Category, PartImage, DonorVehicleImage
        )
    except Exception as e:
        print(f"ОШИБКА ИМПОРТА ВНУТРИ ЗАДАЧИ: {e}")
        raise
    self.update_state(state='PROGRESS', meta={'stage': 'Запуск обновления...'})     #Вывод ошибки в Worker'е и покажет, что именно не так

    print("--- НАЧАЛО: Скачивание и обработка файлов ---")
    fetch_and_prepare_donors(mock_stdout, CATEGORY_MAPPING, GENERATION_MODELS)
    fetch_and_prepare_parts(mock_stdout, CATEGORY_MAPPING, GENERATION_MODELS)
    print("--- ЗАВЕРШЕНО: Файлы Excel подготовлены ---")
    self.update_state(state='PROGRESS', meta={'stage': 'Подготовка файлов завершена. Начало импорта в БД.'})

    print("--- НАЧАЛО: Импорт данных в базу ---")
    import_donors_to_db(mock_stdout, CarMake, CarModel, CarGeneration, DonorVehicle, DonorVehicleImage,
                        TRANSMISSION_MAP)
    import_parts_to_db(mock_stdout, CarMake, CarModel, CarGeneration, DonorVehicle, Category, PartSubCategory,
                       Part, PartImage, CATEGORY_SLUG_MAP)
    print("--- ЗАВЕРШЕНО: Импорт данных в базу ---")

    return {'status': 'SUCCESS', 'result': 'Обновление каталога полностью завершено!'}