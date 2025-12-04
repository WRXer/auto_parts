from django.core.management.base import BaseCommand
from spare_parts.management.fetch_prepare_donors import fetch_and_prepare_donors
from spare_parts.management.fetch_prepare_parts import fetch_and_prepare_parts
from spare_parts.management.import_to_db import import_donors_to_db, import_parts_to_db


class Command(BaseCommand):
    help = 'Запускает скачивание, обработку и обновление каталога в модульной структуре.'

    def handle(self, *args, **options):
        try:    #Импорт Django-зависимостей внутри handle()
            from spare_parts.category_mapping import TRANSMISSION_MAP, CATEGORY_SLUG_MAP, CATEGORY_MAPPING, \
                GENERATION_MODELS
            from spare_parts.models import (
                CarMake, CarModel, CarGeneration, PartSubCategory, Part,
                DonorVehicle, Category, PartImage, DonorVehicleImage
            )
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"❌ Критическая ошибка импорта Django-зависимостей: {e}"))
            return

        self.stdout.write(self.style.WARNING('\n 1/2. НАЧАЛО: Скачивание и обработка файлов Excel '))    #Скачивание и подготовка файлов

        fetch_and_prepare_donors(self.stdout, self.style, CATEGORY_MAPPING, GENERATION_MODELS)    #Вызов функции для ДОНОРОВ
        fetch_and_prepare_parts(self.stdout, self.style, CATEGORY_MAPPING, GENERATION_MODELS)    #Вызов функции для ЗАПЧАСТЕЙ

        self.stdout.write(self.style.WARNING(' 1/2. ЗАВЕРШЕНО: Файлы Excel подготовлены \n'))
        self.stdout.write(self.style.WARNING(' 2/2. НАЧАЛО: Импорт данных в базу Django'))

        import_donors_to_db(self.stdout, self.style, CarMake, CarModel, CarGeneration, DonorVehicle, DonorVehicleImage,
                            TRANSMISSION_MAP)   #Импорт доноров в БД
        import_parts_to_db(self.stdout, self.style, CarMake, CarModel, CarGeneration, DonorVehicle, Category,
                           PartSubCategory, Part, PartImage, CATEGORY_SLUG_MAP)    #Импорт запчастей в БД

        self.stdout.write(self.style.WARNING('\n 2/2. ЗАВЕРШЕНО: Импорт данных в базу '))
        self.stdout.write(self.style.SUCCESS('Обновление каталога полностью завершено! '))