from django import forms


class CartAddPartForm(forms.Form):
    """
    Форма для выбора количества товара, добавляемого в корзину.
    """
    quantity = forms.IntegerField(
        min_value=1,
        max_value=99,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'})
    )

    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )    #Флаг для перезаписи количества (используется при обновлении в самой корзине)