import json
import requests
from django.conf import settings
from orders.models import TelegramAdmin


def get_telegram_admins():
    """
    Получаем список активных объектов TelegramAdmin
    :return:
    """
    return TelegramAdmin.objects.filter(is_active=True)

def send_telegram_notification(message):
    """
    Функция отправки сообщения
    :param message:
    :return:
    """
    token = settings.TELEGRAM_BOT_TOKEN
    admins = get_telegram_admins()

    if not token:
        print("TELEGRAM_BOT_TOKEN is not configured.")
        return
    if not admins.exists():
        print("No active Telegram admins found in database.")
        return

    base_url = f"https://api.telegram.org/bot{token}/sendMessage"

    for admin in admins:
        chat_id = admin.chat_id

        params = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'    #Используем HTML для форматирования (жирный шрифт и т.д.)
        }

        try:
            response = requests.post(base_url, data=params, timeout=5)
            response.raise_for_status()
            print(f"Notification sent successfully to {admin.name} (ID: {chat_id})")
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to send Telegram notification to {admin.name}: {e}")
            return None
