import uuid
import pandas as pd
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from django.conf import settings


DONOR_FILE = settings.BASE_DIR / "donor_cars.xlsx"
PARTS_FILE = settings.BASE_DIR / "catalog_parts.xlsx"
NEW_MODEL_COLUMN_NAME = 'Модель_Базовая'
NEW_GENERATION_COLUMN_NAME = 'Поколение_Число'


def import_donors_to_db(stdout, CarMake, CarModel, CarGeneration, DonorVehicle, DonorVehicleImage,
                        TRANSMISSION_MAP):
    """
    Импорт донорских автомобилей из Excel в БД.
    """
    try:
        df = pd.read_excel(DONOR_FILE)    #Импорт доноров из предыдущего ответа, использующая DONOR_FILE
    except FileNotFoundError:
        stdout.write(f"❌ Ошибка: Файл доноров не найден по пути {DONOR_FILE}. Пропуск импорта.")
        return
    donors_created = 0
    for idx, row in df.iterrows():
        excel_row_num = idx + 2
        donor_id_source = str(row.get('Номер', '')).upper().strip()

        try:
            with transaction.atomic():
                make_name = str(row.get('Марка', '')).upper().strip()
                if not make_name: continue
                make_obj, _ = CarMake.objects.get_or_create(name=make_name)

                model_name = str(row.get(NEW_MODEL_COLUMN_NAME, '')).upper().strip()
                if not model_name: continue
                model_obj, _ = CarModel.objects.get_or_create(make=make_obj, name=model_name)

                generation_name = str(row.get(NEW_GENERATION_COLUMN_NAME, '')).strip()
                if not generation_name or generation_name.lower() in ['nan', 'none', 'n/a', '']: generation_name = "1"

                gen_obj, _ = CarGeneration.objects.get_or_create(model=model_obj, name=generation_name)

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

                photo_urls = set([url.strip() for url in str(row.get('Фото', '')).split(',') if url.strip()])

                current_images_queryset = DonorVehicleImage.objects.filter(donor_vehicle=donor_vehicle_obj)
                current_image_urls = set(current_images_queryset.values_list('image_url', flat=True))

                urls_to_create = photo_urls - current_image_urls    #Определяем URL для создания (в Excel, но нет в DB)
                urls_to_delete = current_image_urls - photo_urls    #Определяем объекты для удаления (в DB, но нет в Excel)

                new_images_to_create = []
                for url in urls_to_create:
                    new_images_to_create.append(
                        DonorVehicleImage(donor_vehicle=donor_vehicle_obj, image_url=url, is_main=False))
                DonorVehicleImage.objects.bulk_create(new_images_to_create)

                current_images_queryset.filter(
                    image_url__in=urls_to_delete).delete()    #Выполняем удаление лишних изображений

                if created:
                    donors_created += 1

        except Exception as e:
            stdout.write(
                f"❌ Критическая ошибка при импорте Донора {donor_id_source} (строка {excel_row_num}): {e}")
    stdout.write(f"Импорт донорских автомобилей в БД завершён! Создано новых: {donors_created}")


def import_parts_to_db(stdout, CarMake, CarModel, CarGeneration, DonorVehicle, Category, PartSubCategory, Part,
                       PartImage, CATEGORY_SLUG_MAP):
    """
    Импорт запчастей из Excel в БД.
    """
    try:
        df = pd.read_excel(PARTS_FILE)    #Импорт запчастей из предыдущего ответа, использующая PARTS_FILE
    except FileNotFoundError:
        stdout.write(f"❌ Ошибка: Файл запчастей не найден по пути {PARTS_FILE}. Пропуск импорта.")
        return
    parts_created = 0
    parts_updated = 0
    for idx, row in df.iterrows():
        excel_row_num = idx + 2
        donor_vehicle_obj = None
        part_unique_id = str(row.get('Артикул', str(uuid.uuid4()))).strip()

        try:
            make_name = str(row.get('Марка', '')).upper().strip()
            if not make_name: continue
            make_obj, _ = CarMake.objects.get_or_create(name=make_name)

            model_name = str(row.get(NEW_MODEL_COLUMN_NAME, '')).upper().strip()
            if not model_name: continue
            model_obj, _ = CarModel.objects.get_or_create(make=make_obj, name=model_name)

            generation_name = str(row.get(NEW_GENERATION_COLUMN_NAME, '')).strip()
            if not generation_name or generation_name.lower() == 'nan': generation_name = "1"

            gen_obj, _ = CarGeneration.objects.get_or_create(model=model_obj, name=generation_name)
            donor_generation_for_part = gen_obj

            donor_raw = str(row.get('Донор', '')).strip()    #Поиск DonorVehicle
            if donor_raw and donor_raw.lower() != 'nan':
                donor_vin_to_lookup = donor_raw.upper().strip()
                try:
                    donor_vehicle_obj = DonorVehicle.objects.get(donor_vin=donor_vin_to_lookup)
                except ObjectDoesNotExist:
                    stdout.write(
                        f"⚠️ Предупреждение: Донор ID '{donor_vin_to_lookup}' (строка {excel_row_num}) не найден.")

            cat_name = row.get('Категория', '').strip()
            cat_name_normalized = (cat_name if cat_name else 'Прочие запчасти').strip()

            try:
                category_obj = Category.objects.get(name__iexact=cat_name_normalized)
            except ObjectDoesNotExist:
                base_cat_slug = CATEGORY_SLUG_MAP.get(cat_name_normalized.upper(), None)
                if not base_cat_slug: base_cat_slug = slugify(cat_name_normalized) or str(uuid.uuid4())[:8]
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
            subcat_obj, _ = PartSubCategory.objects.get_or_create(title=subcat_name,
                                                                  defaults={'category': category_obj, 'slug': slug})
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
                    'donor_vehicle': donor_vehicle_obj,
                }
            )
            part_obj.car_generations.set([gen_obj])

            photo_urls = set([url.strip() for url in str(row.get('Фото', '')).split(',') if url.strip()])
            current_images_queryset = PartImage.objects.filter(part=part_obj)
            current_image_urls = set(current_images_queryset.values_list('image_url', flat=True))

            urls_to_create = photo_urls - current_image_urls    #Определяем URL для создания (в Excel, но нет в DB)
            urls_to_delete = current_image_urls - photo_urls    #Определяем объекты для удаления (в DB, но нет в Excel)

            new_images_to_create = []
            for url in urls_to_create:
                new_images_to_create.append(PartImage(part=part_obj, image_url=url, is_main=False))
            PartImage.objects.bulk_create(new_images_to_create)

            current_images_queryset.filter(
                image_url__in=urls_to_delete).delete()    #Выполняем удаление лишних изображений

            if created:
                parts_created += 1
            else:
                parts_updated += 1

        except Exception as e:
            stdout.write(
                f"❌ Критическая ошибка при обработке строки {excel_row_num} (ID: {part_unique_id}): {e}")
            pass

    stdout.write("Импорт завершён!")
    stdout.write(f"Создано новых запчастей: {parts_created}")
    stdout.write(f"Обновлено существующих запчастей: {parts_updated}")