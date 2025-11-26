import uuid
import pandas as pd
from django.utils.text import slugify
import django, os
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from spare_parts.category_mapping import TRANSMISSION_MAP, CATEGORY_SLUG_MAP
from spare_parts.models import (CarMake, CarModel, CarGeneration, PartSubCategory,Part, DonorVehicle, Category, PartImage, DonorVehicleImage)


DONOR_FILE = 'donor_cars.xlsx'
PARTS_FILE = 'catalog_parts.xlsx'


MODEL_BASE_COL = 'Модель_Базовая'
GEN_COL = 'Поколение_Число'
CAT_COL = 'Категория'


def import_donor_vehicles():
    """
    Первый шаг: Импорт донорских автомобилей.
    Использует колонку 'Номер' / 'НомерПоставкаСтатус' для Donor_VIN,
    извлекая только первый токен для совпадения с файлом запчастей.
    """
    try:
        df = pd.read_excel(DONOR_FILE)
        for col in ['Марка', 'Модель', 'Кузов']:
            if col in df.columns:
                df[col] = df[col].astype(str)     #Предварительная нормализация колонок
    except FileNotFoundError:
        print(f"Ошибка: Файл доноров не найден по пути {DONOR_FILE}")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла доноров: {e}")
        return
    print(f"Начинаю импорт {len(df)} донорских автомобилей...")
    donors_created = 0

    for idx, row in df.iterrows():
        excel_row_num = idx + 2

        #УНИФИКАЦИЯ ID ДОНОРА
        #Извлекаем ID (первый токен) из 'Номер' или 'НомерПоставкаСтатус'
        if 'Номер' in df.columns:
            donor_id_source = str(row.get('Номер', '')).upper().strip()
        try:
            with transaction.atomic():
                make_name = str(row.get('Марка', '')).upper().strip()
                if not make_name or make_name.lower() in ['nan', 'none', 'n/a']:
                    print(f"❌ Пропуск донора {donor_id_source} (строка {excel_row_num}): Отсутствует Марка.")
                    continue
                make_obj, _ = CarMake.objects.get_or_create(name=make_name)

                model_name = str(row.get('Модель_Базовая', '')).upper().strip()
                if not model_name or model_name.lower() in ['nan', 'none', 'n/a']:
                    print(f"❌ Пропуск донора {donor_id_source} (строка {excel_row_num}): Отсутствует Модель.")
                    continue
                model_obj, _ = CarModel.objects.get_or_create(make=make_obj, name=model_name)

                generation_name = str(row.get('Поколение_Число', '')).strip()
                if not generation_name or generation_name.lower() in ['nan', 'none', 'n/a', '']:
                    generation_name = "1"

                gen_obj, _ = CarGeneration.objects.get_or_create(
                    model=model_obj,
                    name=generation_name,
                )

                transmission_raw = str(row.get('Тип КПП (/automatic/manual/variator)', '')).upper().strip()
                transmission_type_key = TRANSMISSION_MAP.get(transmission_raw, None)

                donor_vehicle_obj, created = DonorVehicle.objects.get_or_create(
                    donor_vin=donor_id_source,
                    defaults={
                        'generation': gen_obj,
                        'description': str(row.get('Описание', '')).strip(),
                        'production_year': str(row.get('Год', '')).strip(),
                        'engine_details': str(row.get('Двигатель', '')).strip(),
                        'color': str(row.get('Цвет', '')).strip(),
                        'transmission_type': transmission_type_key
                    }
                )

                photo_urls = [url.strip() for url in str(row.get('Фото', '')).split(',') if url.strip()]
                for url in photo_urls:
                    DonorVehicleImage.objects.get_or_create(donor_vehicle=donor_vehicle_obj,image_url=url,defaults={'is_main': False})

                if created:
                    donors_created += 1

        except IntegrityError as e:
            print(f"❌ Ошибка уникальности Донора {donor_id_source} (строка {excel_row_num}): {e}")
        except Exception as e:
            print(f"❌ Критическая ошибка при импорте Донора {donor_id_source} (строка {excel_row_num}): {e}")

    print("-" * 30)
    print(f"Импорт донорских автомобилей завершён! Создано новых: {donors_created}")
    print("-" * 30)


def import_parts():
    try:
        df = pd.read_excel(PARTS_FILE)
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути {PARTS_FILE}")
        return

    print(f"Начинаю импорт {len(df)} записей...")

    parts_created = 0
    parts_updated = 0

    for idx, row in df.iterrows():
        excel_row_num = idx + 2    #Предполагая, что строка 1 - это заголовки
        donor_vehicle_obj = None    #Инициализация объекта донора (None по умолчанию)

        part_unique_id = str(row.get('Артикул', str(uuid.uuid4()))).strip()

        try:
            make_name = str(row.get('Марка', '')).upper().strip()
            if not make_name:
                print(f"❌ Пропуск строки {excel_row_num}: Отсутствует Марка.")
                continue
            make_obj, _ = CarMake.objects.get_or_create(name=make_name)

            model_name = str(row.get('Модель_Базовая', '')).upper().strip()
            if not model_name:
                print(f"❌ Пропуск строки {excel_row_num}: Отсутствует Модель.")
                continue
            model_obj, _ = CarModel.objects.get_or_create(make=make_obj, name=model_name)

            generation_name = str(row.get('Поколение_Число', '')).strip()
            if not generation_name or generation_name.lower() == 'nan':
                generation_name = "1"

            gen_obj, _ = CarGeneration.objects.get_or_create(
                model=model_obj,
                name=generation_name,
            )

            donor_generation_for_part = gen_obj

            donor_raw = str(row.get('Донор', '')).strip()
            if donor_raw and donor_raw.lower() != 'nan':
                donor_vin_to_lookup = donor_raw.upper().strip()
                try:
                    donor_vehicle_obj = DonorVehicle.objects.get(donor_vin=donor_vin_to_lookup)
                except DonorVehicle.DoesNotExist:
                    print(
                        f"Предупреждение: Донор ID '{donor_vin_to_lookup}' для запчасти в строке {excel_row_num} не найден в базе. Пропуск ссылки.")
                except Exception as e:
                    print(f"Ошибка при поиске Донора ID {donor_vin_to_lookup} в строке {excel_row_num}: {e}")

            cat_name = row.get('Категория', '').strip()
            cat_name_normalized = (cat_name if cat_name else 'Прочие запчасти').strip()

            try:
                category_obj = Category.objects.get(name__iexact=cat_name_normalized)
            except ObjectDoesNotExist:

                base_cat_slug = CATEGORY_SLUG_MAP.get(cat_name_normalized.upper(), None)
                if not base_cat_slug:
                    base_cat_slug = str(uuid.uuid4())[:8]
                cat_slug = base_cat_slug
                cat_counter = 1
                while Category.objects.filter(slug=cat_slug).exists():
                    unique_suffix = f"-{cat_counter}" if cat_counter > 0 else ""
                    cat_slug = f"{base_cat_slug}{unique_suffix}"
                    cat_counter += 1
                category_obj = Category.objects.create(name=cat_name_normalized, slug=cat_slug)

            subcat_name = str(row.get('Наименование', '')).strip() or f'Подкатегория_{uuid.uuid4().hex[:6]}'
            base_slug = slugify(subcat_name) or str(uuid.uuid4())[:8]
            slug = base_slug
            counter = 1
            while PartSubCategory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            subcat_obj, _ = PartSubCategory.objects.get_or_create(title=subcat_name,defaults={'category': category_obj, 'slug': slug})
            part_number = str(row.get('Номер производителя', '')).strip()

            part_obj, created = Part.objects.update_or_create(
                part_id=part_unique_id,
                defaults={
                    'title': str(row.get('Наименование', '')).strip(),
                    'description': str(row.get('Комментарий', '')).strip(),
                    'part_number': part_number,
                    'category': category_obj,
                    'subcategory': subcat_obj,
                    'price': row.get('Цена', 0),
                    'condition': str(row.get('Состояние', 'used')).strip(),
                    'donor_generation': donor_generation_for_part,
                    'donor_vehicle': donor_vehicle_obj,  # Будет None, если Донор пропущен/некорректен
                }
            )
            part_obj.car_generations.set([gen_obj])

            photo_urls = [url.strip() for url in str(row.get('Фото', '')).split(',') if url.strip()]
            for url in photo_urls:
                PartImage.objects.get_or_create(part=part_obj,image_url=url,defaults={'is_main': False})

            if created:
                parts_created += 1
            else:
                parts_updated += 1

        except ObjectDoesNotExist as e:
            print(f"❌ Пропуск строки {excel_row_num} (ID: {part_unique_id}): Ошибка поиска связанного объекта - {e}")
            pass
        except IntegrityError as e:
            print(
                f"❌ Пропуск строки {excel_row_num} (ID: {part_unique_id}): Ошибка уникальности/целостности данных - {e}")
            pass
        except Exception as e:
            print(f"❌ Критическая ошибка при обработке строки {excel_row_num} (ID: {part_unique_id}): {e}")
            pass

    print("Импорт завершён!")
    print(f"Создано новых запчастей: {parts_created}")
    print(f"Обновлено существующих запчастей: {parts_updated}")



if __name__ == "__main__":
    import_donor_vehicles()    #Импортируем доноров
    import_parts()   #Импортируем запчасти