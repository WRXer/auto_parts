from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CreateOrderForm
from carts.cart import Cart
from .models import Order, OrderItem
from django.http import JsonResponse


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
                    OrderItem.objects.create(
                        order=order,
                        part=item['part'],
                        price=item['price'],
                        quantity=item['quantity']
                    )
                cart.clear()
                return JsonResponse({
                    'success': True,
                    'redirect_url': f'/orders/success/{order.id}/'  # Или используйте reverse в коде
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
    return redirect('carts:cart_detail')

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