from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
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

    return render(request, 'carts/cart_detail.html', {'cart': cart})