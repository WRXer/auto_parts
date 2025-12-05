from django.contrib.auth import get_user_model
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from spare_parts.models import Part


User = get_user_model()


class OrderItemQueryset(models.QuerySet):
    def total_price(self):
        return sum(item['price'] * item['quantity']
                   for item in self.cart.values())

    def total_quantity(self):
        """
        Возвращает общее количество товаров (сумму всех quantity).
        """
        return sum(item['quantity'] for item in self.cart.values())


class Order(models.Model):
    STATUS_NEW = 'NEW'
    STATUS_PROCESSING = 'PRC'
    STATUS_PAY = 'PAY'
    STATUS_PREPARING_FOR_SHIPMENT = 'SPS'
    STATUS_SHIPPED = 'SHP'
    STATUS_COMPLETED = 'CMP'
    STATUS_CANCELED = 'CNC'


    STATUS_CHOICES = [
        (STATUS_NEW, 'Новый'),
        (STATUS_PROCESSING, 'В обработке'),
        (STATUS_PAY, 'Ожидает оплаты'),
        (STATUS_PREPARING_FOR_SHIPMENT, 'Готовится к отправке'),
        (STATUS_SHIPPED, 'Отправлен'),
        (STATUS_COMPLETED, 'Выполнен'),
        (STATUS_CANCELED, 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Пользователь")
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания заказа")
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    email = models.EmailField(verbose_name="Email")
    phone = PhoneNumberField(max_length=20, verbose_name="Номер телефона")
    requires_delivery = models.BooleanField(default=False, verbose_name='Требуется доставка')
    delivery_address = models.CharField(max_length=100, verbose_name="Адрес доставки")
    is_paid = models.BooleanField(default=False, verbose_name="Оплачен")
    status = models.CharField(max_length=30,choices=STATUS_CHOICES,default=STATUS_NEW,verbose_name="Статус заказа")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ('-created_timestamp',)

    def get_total_price(self):
        """
        Суммирует стоимость всех позиций в заказе.
        """
        return sum(item.price * item.quantity for item in self.items.all())

    def __str__(self):
        return f"Заказ №{self.pk} от {self.first_name}{self.last_name} ({self.status})"


class OrderItem(models.Model):
    """
    Модель для хранения одной позиции в заказе.
    """
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items',verbose_name="Заказ")
    part = models.ForeignKey(Part, on_delete=models.SET_DEFAULT, null=True, verbose_name='Запчасть', default=None)
    name = models.CharField(max_length=150, verbose_name="Название запчасти")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена на запчасть")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата продажи заказа")


    class Meta:
        verbose_name = "Позиция в заказе"
        verbose_name_plural = "Позиции в заказе"

    objects = OrderItemQueryset.as_manager()

    def __str__(self):
        return f"{self.name} ({self.quantity} шт.) в Заказе №{self.order.pk}"


class TelegramAdmin(models.Model):
    """
    Модель для хранения Telegram Chat ID администраторов/менеджеров,
    получающих уведомления о заказах.
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Имя получателя (для идентификации)"
    )
    chat_id = models.BigIntegerField(
        unique=True,
        verbose_name="Chat ID Telegram"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен"
    )

    class Meta:
        verbose_name = "Администратор Telegram"
        verbose_name_plural = "Администраторы Telegram"

    def __str__(self):
        return f"{self.name} (ID: {self.chat_id})"
