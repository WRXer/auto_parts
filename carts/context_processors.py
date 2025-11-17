from .cart import Cart


def carts(request):
    """
    Добавляет объект корзины в контекст шаблона
    под ключом 'cart'.
    """
    return {'cart': Cart(request)}