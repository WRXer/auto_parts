from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from orders.forms import CreateOrderForm
from spare_parts.models import Part
from .cart import Cart
from .forms import CartAddPartForm


@require_POST
def cart_add(request, part_id):
    """
    Добавляет или обновляет запчасть в корзине.
    """
    cart = Cart(request)
    part = get_object_or_404(Part, pk=part_id)    #Ищем по ID запчасти
    form = CartAddPartForm(request.POST)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(part=part, quantity=cd['quantity'], override_quantity=cd['override'])
        request.session.save()
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': 'Товар добавлен!',
                'total_quantity': cart.get_total_quantity()
            })
        return redirect('carts:cart_detail')
    else:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            }, status=400)
        return redirect('carts:cart_detail')

@require_POST
def cart_remove(request, part_id):
    """
    Удаляет запчасть из корзины.
    """
    cart = Cart(request)
    part = get_object_or_404(Part, id=part_id)
    cart.remove(part)
    return redirect('carts:cart_detail')


def cart_detail(request):
    """
    Отображает содержимое корзины.
    """
    cart = Cart(request)
    initial_data = {}
    if request.user.is_authenticated:
        user = request.user
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': getattr(user, 'phone', ''),
        }
    order_form = CreateOrderForm(initial=initial_data, user=request.user)    #Создаем заполненную форму заказа
    context = {
        'cart': cart,
        'form': order_form,    #Теперь форма доступна в контексте
    }
    return render(request, 'carts/cart_detail.html', context)    #Убедитесь, что имя шаблона верное