import pandas as pd
import requests
import os, re, io
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()
DONOR_URL = os.getenv('DONOR_URL')
DONOR_FILE = settings.BASE_DIR / "donor_cars.xlsx"

MODEL_COLUMN_NAME = 'Модель'
BODY_COLUMN_NAME = 'Кузов'
NEW_MODEL_COLUMN_NAME = 'Модель_Базовая'
NEW_GENERATION_COLUMN_NAME = 'Поколение_Число'


def _get_generation_mapping(GENERATION_MODELS):
    return {re.sub(r'\s+', ' ', m).strip().lower() for m in GENERATION_MODELS}


def _get_flat_category_mapping(CATEGORY_MAPPING):
    FLAT_MAPPING = {}
    for code, info in CATEGORY_MAPPING.items():
        for sub in info['subcategories']:
            FLAT_MAPPING[sub.lower().strip()] = {'code': code, 'title': info['title']}
    return FLAT_MAPPING


def fetch_and_prepare_donors(stdout, CATEGORY_MAPPING, GENERATION_MODELS):
    """
    Скачивает, обрабатывает и сохраняет файл донорских автомобилей.
    """
    GENERATION_MODELS_SET = _get_generation_mapping(GENERATION_MODELS)
    FLAT_MAPPING = _get_flat_category_mapping(CATEGORY_MAPPING)

    def extract_model_generation(full_model_str):
        if not isinstance(full_model_str, str): return full_model_str, None
        normalized_model = re.sub(r'\s+', ' ', full_model_str).strip()
        normalized_model_lower = normalized_model.lower()
        if normalized_model_lower in GENERATION_MODELS_SET:
            model_gen_match = re.search(r'^(.*?)\s*(\d+)$', normalized_model)
            if model_gen_match:
                return model_gen_match.group(1).strip(), model_gen_match.group(2)
        return full_model_str, None

    def get_category_info(product_name):
        if not isinstance(product_name, str): return 'OTHER', 'Прочие запчасти'
        name_clean = re.sub(r'[^\w\s]', '', product_name).strip().lower()
        if name_clean in FLAT_MAPPING:
            return FLAT_MAPPING[name_clean]['code'], FLAT_MAPPING[name_clean]['title']
        return 'OTHER', 'Прочие запчасти'

    if os.path.exists(DONOR_FILE):
        try:
            os.remove(DONOR_FILE)
            stdout.write(f"🗑️ Старый файл '{DONOR_FILE}' удален.")
        except OSError as e:
            stdout.write(f"❌ Ошибка при удалении файла '{DONOR_FILE}': {e}")
            return

    stdout.write(f"Скачиваю файл с донорскими автомобилями с {DONOR_URL}...")
    try:
        response = requests.get(DONOR_URL)
        response.raise_for_status()
        content = response.content.decode('utf-8') if 'utf-8' in response.headers.get('content-type',
                                                                                      '').lower() else response.content.decode(
            'windows-1251')
        stdout.write("Файл скачан. Начинаю обработку...")
        df = pd.read_csv(io.StringIO(content), delimiter=';')

        if BODY_COLUMN_NAME in df.columns:
            df[BODY_COLUMN_NAME] = df[BODY_COLUMN_NAME].fillna('1')
            df[BODY_COLUMN_NAME] = df[BODY_COLUMN_NAME].astype(str).str.strip().replace(
                {'': '1', 'none': '1', 'nan': '1'}, regex=False)
            stdout.write(f"Обработка '{BODY_COLUMN_NAME}' завершена.")
        else:
            df[BODY_COLUMN_NAME] = '1'

        if MODEL_COLUMN_NAME in df.columns:
            df[[NEW_MODEL_COLUMN_NAME, NEW_GENERATION_COLUMN_NAME]] = df[MODEL_COLUMN_NAME].apply(
                lambda x: pd.Series(extract_model_generation(x)))
        else:
            df[NEW_MODEL_COLUMN_NAME] = 'N/A'
            df[NEW_GENERATION_COLUMN_NAME] = 'N/A'

        if NEW_GENERATION_COLUMN_NAME in df.columns and BODY_COLUMN_NAME in df.columns:
            is_generation_missing = df[NEW_GENERATION_COLUMN_NAME].isna()
            df.loc[is_generation_missing, NEW_GENERATION_COLUMN_NAME] = df.loc[is_generation_missing, BODY_COLUMN_NAME]

        if NEW_GENERATION_COLUMN_NAME in df.columns:
            numeric_series = pd.to_numeric(df[NEW_GENERATION_COLUMN_NAME], errors='coerce')
            df[NEW_GENERATION_COLUMN_NAME] = numeric_series.apply(lambda x: str(int(x)) if pd.notna(x) else None)

        if 'Наименование' in df.columns:
            df['Категория'] = df['Наименование'].apply(lambda x: get_category_info(x)[1])

        df.to_excel(DONOR_FILE, index=False)
        stdout.write(f"✅ Файл доноров сохранен как: {DONOR_FILE}")

    except Exception as e:
        stdout.write(f"❌ ОШИБКА при обработке доноров: {e}")