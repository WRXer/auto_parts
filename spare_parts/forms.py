import uuid

from django import forms
from spare_parts.models import DonorVehicle, Part


class PartAdminForm(forms.ModelForm):
    """
    Кастомная форма для запчасти, добавляющая поле для пакетного ввода URL.
    """
    # Новое поле для пакетного ввода URL фотографий
    bulk_url_input = forms.CharField(
        label="Пакетный ввод URL фотографий (для этой Запчасти)",
        required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'URL-адреса через запятую, пробел или новую строку.'}),
        help_text="Все ссылки будут добавлены как новые фото для этой запчасти. Первое фото станет главным, если главные фото не заданы вручную."
    )

    class Meta:
        model = Part
        fields = '__all__'

    def clean_part_id(self):
        """
        Автозаполнение внутреннего артикула продавца
        :return:
        """
        id = self.cleaned_data.get('part_id')
        if not id:    #Если поле пустое (или None), генерируем новый ID
            id = uuid.uuid4().hex[:8].upper()    #Гарантируем уникальность и краткость
            if Part.objects.filter(part_id=id).exists():    #Проверяем уникальность, чтобы избежать конфликтов при ручной генерации
                return self.clean_part_id()    #Если сгенерированный ID уже есть, генерируем заново
        return id

    def save(self, commit=True):
        instance = super().save(commit=False)    #Получаем экземпляр Part (еще не в БД)
        donor = self.cleaned_data.get('donor_generation')    #Получаем донора из 'cleaned_data'
        selected_gens = self.cleaned_data.get('car_generations', [])    #Получаем список выбранных пользователем авто из 'cleaned_data'
        final_gens = list(selected_gens)    #Превращаем в Python-список
        if donor and (donor not in final_gens):    #Добавляем донора в список, если его там нет
            final_gens.append(donor)
        self.cleaned_data['car_generations'] = final_gens    #Перезаписываем 'cleaned_data' нашим новым списком.
        if commit:
            instance.save()    #Теперь мы вызываем оригинальный метод save(), который сохранит и инстанс, и M2M-поля, но M2M он возьмет уже из нашего измененного cleaned_data.
            self.save_m2m()    #Сохраняем M2M, используя обновленные cleaned_data
        return instance



class DonorVehicleAdminForm(forms.ModelForm):
    bulk_url_input = forms.CharField(
        label="Пакетный ввод URL фотографий",
        required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Вставьте URL-адреса здесь, разделяя запятыми, пробелами или переносами строки.'}),
        help_text="Все ссылки будут добавлены как новые фото. Первое фото станет главным, если главные фото не заданы."
    )

    class Meta:
        model = DonorVehicle
        fields = '__all__'