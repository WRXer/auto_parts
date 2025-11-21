import sys
import django
import pandas as pd
import requests
import os, re, io
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from spare_parts.category_mapping import CATEGORY_MAPPING, GENERATION_MODELS


GENERATION_MODELS_SET = {re.sub(r'\s+', ' ', m).strip().lower() for m in GENERATION_MODELS}


def extract_model_generation(full_model_str):
    """
    Разделяет полную строку модели на базовую модель и поколение,
    если она присутствует в списке GENERATION_MODELS_SET.
    """
    if not isinstance(full_model_str, str):
        return full_model_str, None
    normalized_model = re.sub(r'\s+', ' ', full_model_str).strip()
    normalized_model_lower = normalized_model.lower()
    if normalized_model_lower in GENERATION_MODELS_SET:
        model_gen_match = re.search(r'^(.*?)\s*(\d+)$', normalized_model)

        if model_gen_match:
            base_model = model_gen_match.group(1).strip()
            generation_key = model_gen_match.group(2)
            return base_model, generation_key
    return full_model_str, None



FLAT_MAPPING = {}    #СОЗДАНИЕ ПЛОСКОГО СЛОВАРЯ (Для категорий)
for code, info in CATEGORY_MAPPING.items():
    for sub in info['subcategories']:
        FLAT_MAPPING[sub.lower().strip()] = {
            'code': code,
            'title': info['title']
        }

def get_category_info(product_name):
    if not isinstance(product_name, str):
        return 'OTHER', 'Прочие запчасти'
    name_clean = re.sub(r'[^\w\s]', '', product_name).strip().lower()
    if name_clean in FLAT_MAPPING:
        return FLAT_MAPPING[name_clean]['code'], FLAT_MAPPING[name_clean]['title']
    return 'OTHER', 'Прочие запчасти'

URL = os.getenv('PARTS_URL')
OUTPUT_FILE = "catalog_parts.xlsx"
MODEL_COLUMN_NAME = 'Модель'
BODY_COLUMN_NAME = 'Кузов'


NEW_MODEL_COLUMN_NAME = 'Модель_Базовая'
NEW_GENERATION_COLUMN_NAME = 'Поколение_Число'

if os.path.exists(OUTPUT_FILE):
    try:
        os.remove(OUTPUT_FILE)
        print(f"🗑️ Старый файл '{OUTPUT_FILE}' удален.")
    except OSError as e:
        print(f"❌ Ошибка при удалении файла '{OUTPUT_FILE}': {e}")
        sys.exit(1)

print(f"Скачиваю файл с {URL}...")
try:
    response = requests.get(URL)
    response.raise_for_status()
    try:
        content = response.content.decode('utf-8')
    except UnicodeDecodeError:
        content = response.content.decode('windows-1251')
    print("Файл скачан. Начинаю обработку...")

    df = pd.read_csv(io.StringIO(content), delimiter=';')

    if BODY_COLUMN_NAME in df.columns:
        print(f"Обрабатываю колонку '{BODY_COLUMN_NAME}' для установки дефолтного значения '1'...")
        df[BODY_COLUMN_NAME] = df[BODY_COLUMN_NAME].fillna('1')
        df[BODY_COLUMN_NAME] = df[BODY_COLUMN_NAME].astype(str).str.strip().replace({'': '1', 'none': '1', 'nan': '1'},regex=False)
        print(f"Дефолтное значение '1' установлено для пустых ячеек в колонке '{BODY_COLUMN_NAME}'.")
    else:
        print(f"Колонка '{BODY_COLUMN_NAME}' не найдена. Создаю ее и заполняю значением '1'.")
        df[BODY_COLUMN_NAME] = '1'


    if MODEL_COLUMN_NAME in df.columns:
        print(f"Обрабатываю колонку '{MODEL_COLUMN_NAME}' для разделения модели/поколения...")
        df[[NEW_MODEL_COLUMN_NAME, NEW_GENERATION_COLUMN_NAME]] = df[MODEL_COLUMN_NAME].apply(
            lambda x: pd.Series(extract_model_generation(x)))
        print("Разделение модели/поколения завершено.")
    else:
        print(f"❌ ВНИМАНИЕ: Колонка '{MODEL_COLUMN_NAME}' не найдена. Создаю заглушки.")
        df[NEW_MODEL_COLUMN_NAME] = df.get(MODEL_COLUMN_NAME, 'N/A')
        df[NEW_GENERATION_COLUMN_NAME] = 'N/A'


    if NEW_GENERATION_COLUMN_NAME in df.columns and BODY_COLUMN_NAME in df.columns:
        print(f"Проверяю колонку '{BODY_COLUMN_NAME}' на наличие поколения...")
        is_generation_missing = df[NEW_GENERATION_COLUMN_NAME].isna()
        transfer_condition = is_generation_missing
        df.loc[transfer_condition, NEW_GENERATION_COLUMN_NAME] = df.loc[transfer_condition, BODY_COLUMN_NAME]
        print("Перенос потенциальных поколений из колонки 'Кузов' в 'Поколение_Число' завершен.")


    cat_codes = []
    cat_titles = []

    for index, row in df.iterrows():
        name = row.get('Наименование', '')
        code, title = get_category_info(name)
        cat_codes.append(code)
        cat_titles.append(title)

    df['Category_Code'] = cat_codes
    df['Категория'] = cat_titles

    print("Сохраняю в Excel...")
    df.to_excel(OUTPUT_FILE, index=False)

    print("-" * 30)
    print(f"✅ ГОТОВО! Файл сохранен как: {OUTPUT_FILE}")
    print(
        f"В файле теперь есть колонки '{BODY_COLUMN_NAME}', '{NEW_MODEL_COLUMN_NAME}', '{NEW_GENERATION_COLUMN_NAME}', 'Category_Code' и 'Категория'.")

except Exception as e:
    print(f"ОШИБКА: {e}")