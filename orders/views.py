from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CreateOrderForm
from carts.cart import Cart
from .models import Order, OrderItem


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
                messages.success(request, f"Заказ №{order.id} успешно оформлен!")
                return redirect('orders:order_success', order_id=order.id)

            except Exception as e:
                error_message = f"Критическая ошибка при оформлении заказа. Детали: {e}"
                messages.error(request, error_message)
                print(f"ERROR: Order creation failed - {e}")    #В случае ошибки базы данных или других сбоев
                return render(request, 'orders/create_order.html', {'cart': cart, 'form': form})    #Возвращаем страницу с формой и ошибкой
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")    #Невалидная форма (ошибки валидации)
            return render(request, 'orders/create_order.html', {'cart': cart, 'form': form})    #Возвращаем страницу с формой и ошибками
    else:
        form = CreateOrderForm()
        return render(request, 'orders/create_order.html', {'cart': cart, 'form': form})    #Возвращаем полный шаблон формы

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