from django import forms

from spare_parts.models import DonorVehicle


class DonorVehicleAdminForm(forms.ModelForm):
    # Новое поле для пакетного ввода URL
    bulk_url_input = forms.CharField(
        label="Пакетный ввод URL фотографий",
        required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Вставьте URL-адреса здесь, разделяя запятыми, пробелами или переносами строки.'}),
        help_text="Все ссылки будут добавлены как новые фото. Первое фото станет главным, если главные фото не заданы."
    )

    class Meta:
        model = DonorVehicle
        fields = '__all__'