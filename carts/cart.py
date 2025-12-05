from django.conf import settings
from spare_parts.models import Part


class Cart:
    def __init__(self, request):
        """
        Инициализация корзины.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
            self.session.modified = True
        self.cart = cart



    def add(self, part, quantity=1, override_quantity=False):
        """
        Добавляет запчасть в корзину или обновляет ее количество.
        """
        part_id = str(part.id)

        if part_id not in self.cart:
            self.cart[part_id] = {'quantity': 0,'price': str(part.price)}
        if override_quantity:
            self.cart[part_id]['quantity'] = quantity
        else:
            self.cart[part_id]['quantity'] += quantity
        self.save()

    def save(self):
        """
        Помечает сессию как измененную для сохранения.
        """
        self.session.modified = True

    def remove(self, part):
        """
        Удаляет запчасть из корзины.
        """
        part_id = str(part.id)
        if part_id in self.cart:
            del self.cart[part_id]
            self.save()

    def __iter__(self):
        """
        Итерируемся по товарам в корзине и получаем объекты Part.
        """
        part_ids = self.cart.keys()
        parts = Part.objects.filter(id__in=part_ids)
        cart = self.cart.copy()
        for part in parts:
            cart[str(part.id)]['part'] = part    #Добавляем объект Part под ключом 'part'

        for item in cart.values():
            item['price'] = float(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Возвращает общее количество товаров в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_quantity(self):
        """
        Возвращает общее количество товаров (сумму всех quantity).
        """
        return self.__len__()

    def get_unique_count(self):
        """
        Возвращает количество уникальных товарных позиций (строк) в корзине.
        """
        return len(self.cart)

    def get_total_price(self):
        """
        Вычисляет общую стоимость всех товаров.
        """
        total = sum(int(float(item['price'])) * item['quantity']
                    for item in self.cart.values())
        return total

    def clear(self):
        """
        Очищает корзину.
        """
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.session.modified = True