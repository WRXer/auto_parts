from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.template.loader import render_to_string
from orders.telegram_notifier import send_telegram_notification
from .forms import CreateOrderForm
from carts.cart import Cart
from .models import Order, OrderItem
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import user_passes_test


def create_order(request):
    """
    Обрабатывает отображение формы заказа (GET) и создание заказа (POST),
    используя стандартный полный рендеринг страницы.
    """
    cart = Cart(request)
    if not cart:
        messages.error(request, "Ваша корзина пуста. Невозможно оформить заказ.")
        return redirect('carts:cart_detail')

    if request.method == 'POST':
        form = CreateOrderForm(request.POST)
        if form.is_valid():
            try:
                order = form.save()
                for item in cart:
                    product_obj = item['part']
                    OrderItem.objects.create(
                        order=order,
                        part=product_obj,
                        name=product_obj.title,
                        price=item['price'],
                        quantity=item['quantity']
                    )
                cart.clear()

                message = (
                    f"🎉 <b>НОВЫЙ ЗАКАЗ # {order.id}</b>\n\n"
                    f"👤 Клиент: {order.first_name} {order.last_name}\n"
                    f"📞 Телефон: {order.phone or 'Не указан'}\n"
                    f"📧 Email: {order.email or 'Не указан'}\n\n"
                    
                    f"🔗 <a href='https://drably-lenient-avocet.cloudpub.ru/profile/'>Посмотреть заказ </a>"
                )
                send_telegram_notification(message)    #Вызов функции рассылки

                success_modal_html = render_to_string(
                    'orders/success_order_modal.html',
                    {'order': order},
                    request=request
                )
                return JsonResponse({
                    'success': True,
                    'modal_html': success_modal_html    #Отправляем HTML клиенту
                })

            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error_message': f'Ошибка создания заказа: {str(e)}'
                })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })

    initial_data = {}
    if request.user.is_authenticated:   #Подставляем данные из профиля авторизованного пользователя
        user = request.user
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.phone,
        }

    form = CreateOrderForm(initial=initial_data, user=request.user)    #Создаем форму, используя initial_data
    modal_html = render_to_string(
        'orders/create_order_modal.html',
        {'form': form, 'cart': cart},    #Передаем заполненную форму и корзину
        request=request
    )
    return JsonResponse({'success': True, 'modal_html': modal_html})

def order_success(request, order_id):
    """
    Отображает страницу с подтверждением заказа.
    """
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'orders/success.html', context)


@user_passes_test(lambda u: u.is_superuser)     #Доступ только для суперпользователей
@require_http_methods(["POST"])
def update_order_status(request, order_id):
    """
    Обновляет статус заказа через AJAX-запрос.
    """
    try:
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        valid_statuses = [status[0] for status in order.STATUS_CHOICES]    #Проверка, что полученный статус корректен

        if new_status and new_status in valid_statuses:
            order.status = new_status
            order.save()
            return JsonResponse({
                'success': True,
                'new_status_display': order.get_status_display(),
                'message': 'Статус заказа успешно обновлен.'
            })
        else:
            return JsonResponse({'success': False, 'error': 'Некорректный статус'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def update_paid_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_paid_status_str = request.POST.get('is_paid')
    new_paid_status = new_paid_status_str == 'True'    #Конвертация строки "True"/"False" в булево значение
    order.is_paid = new_paid_status
    order.save()
    return JsonResponse({'success': True, 'is_paid': new_paid_status, 'message': 'Статус оплаты обновлен.'})