from django.contrib import admin
from decimal import Decimal
from .models import Order, OrderItem



class OrderItemInline(admin.TabularInline):
    """
    Создаем инлайн-класс для позиций заказа, чтобы редактировать их прямо внутри заказа
    """
    model = OrderItem
    raw_id_fields = ('part',)
    fields = ('part', 'name', 'price', 'quantity', 'subtotal')
    readonly_fields = ('name', 'subtotal')
    extra = 0

    def subtotal(self, instance):
        """
        Отображение итоговой суммы для позиции (берется из свойства модели).
        """
        return instance.subtotal
    subtotal.short_description = 'Итог'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Методы для отображения общей суммы
    """
    def total_price(self, obj):
        """
        Отображение общей суммы заказа, используя OrderItem QuerySet.
        """
        total = sum(item.price * Decimal(item.quantity) for item in obj.items.all())
        return f"{total:,.2f}"

    total_price.short_description = 'Общая сумма'

    list_display = (
        'pk', 'first_name', 'last_name', 'phone', 'email', 'status',
        'is_paid', 'requires_delivery', 'total_price', 'created_timestamp'
    )
    list_filter = ('status', 'is_paid', 'requires_delivery', 'created_timestamp')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'delivery_address')

    fieldsets = (
        ('Информация о пользователе и статусе', {
            'fields': ('user', 'status', 'is_paid'),
        }),
        ('Контактная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone'),
        }),
        ('Доставка', {
            'fields': ('requires_delivery', 'delivery_address'),
            'description': "Адрес заполняется только при включенной доставке."
        }),
        ('Итог и даты', {
            'fields': ('total_price', 'created_timestamp', 'updated_at'),
            'description': "Общая сумма рассчитывается автоматически."
        }),
    )

    readonly_fields = ('created_timestamp', 'updated_at', 'total_price')
    inlines = [OrderItemInline]     #Добавляем OrderItemInline, чтобы видеть товары в заказе

    def get_form(self, request, obj=None, **kwargs):
        """
        Делаем поле user необязательным (для гостевых заказов)
        """
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['user'].required = False
        return form