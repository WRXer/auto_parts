import uuid
from django.utils.safestring import mark_safe
from django import forms
from django.contrib import admin
from spare_parts.models import Part, CarGeneration, CarMake, CarModel, Category, PartImage, DonorVehicle, \
    DonorVehicleImage


class PartImageInline(admin.TabularInline):
    """
    Форма добавления изображений в виде таблицы.
    """
    model = PartImage
    fields = ('image', 'image_url', 'is_main', 'image_preview')
    readonly_fields = ('image_preview',)    #Предпросмотр не должен быть редактируемым
    extra = 1    #Одна пустая строка для добавления нового фото
    verbose_name_plural = "Фотографии (Файл ИЛИ URL)"

    def image_preview(self, obj):
        """
        Отображает миниатюру по URL (если есть) или по загруженному файлу.
        """
        source = obj.get_image_source()
        if source:
            return mark_safe(f'<img src="{source}" style="max-height: 100px; max-width: 150px; border-radius: 4px;" />')
        return "Нет изображения"     #mark_safe позволяет Django отобразить HTML-тег <img>
    image_preview.short_description = 'Предпросмотр'


class DonorVehicleImageInline(admin.TabularInline):
    """
    Позволяет добавлять несколько изображений к конкретной машине-донору
    прямо на странице ее редактирования.
    """
    model = DonorVehicleImage
    extra = 1
    fields = ('image', 'image_url', 'is_main', 'image_preview')
    readonly_fields = ('image_preview',)
    extra = 1
    verbose_name_plural = "Фотографии Донора (Файл ИЛИ URL)"

    def image_preview(self, obj):
        source = obj.get_image_source()    #Используем универсальный метод
        if source:
            return mark_safe(f'<img src="{source}" style="max-height: 50px; max-width: 70px; border-radius: 4px;" />')
        return "Нет фото"

    image_preview.short_description = 'Предпросмотр'


@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('make', 'name')

@admin.register(CarGeneration)
class CarGenerationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'year_start', 'year_end')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class PartAdminForm(forms.ModelForm):
    """
    Кастомная форма, которая гарантирует, что
    донор будет добавлен в M2M перед сохранением.
    """
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
            instance.save()   #Теперь мы вызываем оригинальный метод save(), который сохранит и инстанс, и M2M-поля, но M2M он возьмет уже из нашего измененного cleaned_data.
            self.save_m2m()  # Сохраняем M2M, используя обновленные cleaned_data
        return instance


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    inlines = [PartImageInline]
    form = PartAdminForm
    list_display = ('title', 'price', 'is_active', 'get_main_image_preview')
    list_filter = ('is_active', 'condition', 'category', 'donor_generation__model__make')
    search_fields = ('title', 'part_number', 'part_id', 'description')
    filter_horizontal = ('car_generations',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related('donor_generation__model__make', 'donor_vehicle').prefetch_related('car_generations__model__make')
        return queryset

    def compatible_auto_list(self, obj):
        full_list = []
        for gen in obj.car_generations.all():
            full_list.append(str(gen))
        return ", ".join(full_list)

    compatible_auto_list.short_description = 'Совместимые авто'

    def get_main_image_preview(self, obj):
        """
        Отображает миниатюру главного изображения в списке запчастей.
        Использует метод get_main_image_source() из модели Part.
        """
        url = obj.get_main_image_source()
        if url:
            return mark_safe(f'<img src="{url}" style="max-height: 50px; max-width: 50px; border-radius: 4px;" />')
        return 'Нет фото'

    get_main_image_preview.short_description = 'Главное фото'


@admin.register(DonorVehicle)
class DonorVehicleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'generation', 'title', 'color', 'engine_details', 'description', 'transmission_type' ,'arrival_date', 'get_image_count')
    list_filter = ('generation__model__make', 'arrival_date')
    search_fields = ('title', 'generation__name')
    inlines = [DonorVehicleImageInline]    #Связываем инлайн-класс с основной моделью

    def get_image_count(self, obj):
        return obj.images.count()

    def get_main_image_preview(self, obj):
        url = obj.get_main_image_source()   #Используем метод из модели DonorVehicle
        if url:
            return mark_safe(f'<img src="{url}" style="max-height: 50px; max-width: 70px; border-radius: 4px;" />')
        return 'Нет фото'

    get_main_image_preview.short_description = 'Главное фото'
    get_image_count.short_description = 'Фото'
