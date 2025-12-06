# ====================================================================
# STAGE 1: BUILD STAGE (Сборка и установка зависимостей)
# ====================================================================
FROM python:3.12-slim-bullseye AS builder

# Установка системных зависимостей, необходимых для компиляции Python-пакетов (например, psycopg2)
# Включает также git для получения зависимостей (если они есть)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /usr/src/app

# Копирование файла требований и установка зависимостей
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# ====================================================================
# STAGE 2: PRODUCTION STAGE (Финальный минимальный образ)
# ====================================================================
FROM python:3.12-slim-bullseye

# Установка системных зависимостей, необходимых ТОЛЬКО для запуска (runtime)
# libpq-dev не нужен, т.к. мы скомпилировали psycopg2 на предыдущем шаге
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /vol/web

# Установка скомпилированных пакетов (колеса)
COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Копирование кода приложения
COPY . /vol/web

# Предоставление прав на выполнение manage.py
RUN chmod +x manage.py

# Установка переменной окружения, чтобы Python сразу писал логи в stdout/stderr
ENV PYTHONUNBUFFERED 1

# Порт, который будет использовать Gunicorn (совпадает с EXPOSE в docker-compose.yml)
EXPOSE 8000

# Рекомендуется использовать команду в docker-compose.yml,
# но можно указать ENTRYPOINT, если он общий для всех сервисов.
# ENTRYPOINT ["/vol/web/entrypoint.sh"]