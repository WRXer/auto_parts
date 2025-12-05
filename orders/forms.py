from django import forms
from django.contrib.auth import get_user_model
from .models import Order


User = get_user_model()


class CreateOrderForm(forms.ModelForm):
    """
    Форма для создания нового заказа.
    Используется для сбора контактной информации и деталей доставки от пользователя.
    """
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически делаем delivery_address необязательным при инициализации
        self.fields['delivery_address'].required = False

        if user and user.is_authenticated:
            self.fields['email'].widget.attrs['readonly'] = True    #Делаем email и phone только для чтения, чтобы пользователь их не менял
            self.fields['phone'].widget.attrs['readonly'] = True


    class Meta:
        model = Order
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'requires_delivery',
            'delivery_address'
        )

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 999-99-99'
            }),
            'delivery_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Город, улица, дом, квартира'
            }),
            'requires_delivery': forms.CheckboxInput(attrs={
                'class': 'form-check-input mt-1 requires-delivery-toggle',
                'id': 'id_requires_delivery'
            }),
        }

        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'phone': 'Телефон',
            'requires_delivery': 'Требуется доставка',
            'delivery_address': 'Адрес доставки',
        }

    def clean_delivery_address(self):
        """
        Метод валидации, который проверяет, что адрес доставки указан,
        если выбрана опция 'Требуется доставка'.
        """
        requires_delivery = self.cleaned_data.get('requires_delivery')
        delivery_address = self.cleaned_data.get('delivery_address')

        if requires_delivery and not delivery_address:
            raise forms.ValidationError("Пожалуйста, укажите адрес доставки, так как вы выбрали доставку.")    #Убеждаемся, что адрес обязателен, если выбрана доставка
        if not requires_delivery and delivery_address:
            return ""
        return delivery_address

    def save(self, commit=True):
        """
        Переопределение метода save:
        1. Создает экземпляр Order (без сохранения в БД).
        2. Проверяет, существует ли пользователь с введенным email.
        3. Если найден, привязывает этого пользователя к заказу (order.user).
        4. Сохраняет заказ, если commit=True.
        """
        order = super().save(commit=False)
        email = self.cleaned_data.get('email')

        if email:
            try:
                user = User.objects.get(email__iexact=email)    #Поиск зарегистрированного пользователя по email
                order.user = user
            except User.DoesNotExist:
                pass    #Если пользователь не найден, order.user останется None (или значением по умолчанию)
        if commit:
            order.save()
        return order

