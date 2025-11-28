from django import forms
from .models import Order


class CreateOrderForm(forms.ModelForm):
    """
    Форма для создания нового заказа.
    Используется для сбора контактной информации и деталей доставки от пользователя.
    """
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
                'class': 'form-check-input mt-1',
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
            raise forms.ValidationError("Пожалуйста, укажите адрес доставки, так как вы выбрали доставку.")

        if not requires_delivery and delivery_address:    #Очищаем поле адреса, если доставка не требуется
            return ""

        return delivery_address