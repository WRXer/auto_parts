import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic import ListView

from orders.telegram_notifier import send_telegram_notification
from spare_parts.models import CarMake, DonorVehicle


class IndexListView(ListView):  # Или ваш существующий класс
    model = CarMake
    template_name = 'main/index.html'
    context_object_name = 'car_makes'

    def get_queryset(self):
        return CarMake.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new_arrivals'] = DonorVehicle.objects.select_related('generation__model__make').prefetch_related('images').order_by('-arrival_date')[:4]
        return context

def about(request):

    return render(request, 'main/about.html')

def contacts(request):
    return render(request, 'main/contacts.html')

def delivery(request):
    return render(request, 'main/delivery.html')

def payment(request):
    return render(request, 'main/payment_info.html')


@csrf_exempt
@require_http_methods(["POST"])
def submit_part_request(request):
    """
    Обрабатывает форму запроса запчасти и отправляет уведомление в Telegram.
    """
    if request.content_type.startswith('application/x-www-form-urlencoded') or \
            request.content_type.startswith('multipart/form-data'):
        name = request.POST.get('name', 'Не указано')
        phone = request.POST.get('phone', 'Не указано')

    elif request.content_type.startswith('application/json'):
        try:
            data = json.loads(request.body)
            name = data.get('name', 'Не указано')
            phone = data.get('phone', 'Не указано')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': 'Неверный формат данных JSON'}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': 'Неподдерживаемый Content-Type'}, status=400)
    if not phone or phone == 'Не указано':    #Валидация
        return JsonResponse({'success': False, 'errors': 'Поле "Телефон" обязательно для заполнения.'}, status=400)

    telegram_message = f"""
    <b>🛎️ НОВЫЙ ЗАПРОС НА ЗВОНОК ПО ПОДБОРУ ЗАПЧАСТИ</b>

    👤 Имя: {name}
    📞 Телефон: <b>{phone}</b>
    """

    result = send_telegram_notification(telegram_message)
    if isinstance(result, dict) and result.get('ok') is True:
        return JsonResponse({'success': True})
    else:
        print(f"DEBUG (500): Telegram API Response was not successful or invalid: {result}")
        return JsonResponse({'success': False, 'errors': 'Ошибка при отправке в Telegram (проверьте логи сервера).'},
                            status=500)