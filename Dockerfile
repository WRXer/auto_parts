FROM python:3.14

# Установка системных зависимостей (для Postgres и других)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    libpq-dev \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование требований и их установка
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего остального кода
COPY . /app/

# Запуск от имени пользователя (лучше для безопасности)
# RUN useradd --no-create-home django_user
# USER django_user

# Открытие порта
EXPOSE 8000

# Команда запуска (будет перезаписана в docker-compose)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]