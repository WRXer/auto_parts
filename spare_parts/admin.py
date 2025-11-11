import uuid

from django import forms
from django.contrib import admin
from spare_parts.models import Part, CarGeneration, CarMake, CarModel, Category, PartImage, DonorVehicle, \
    DonorVehicleImage


class PartImageInline(admin.TabularInline):
    """Отображает форму добавления изображений в виде таблицы."""
    model = PartImage
    extra = 1    #Количество пустых форм для добавления новых изображений
    fields = ('image', 'is_main')
    # Позволяем показывать миниатюры в админке (требует написания метода)
    # readonly_fields = ['get_image_preview']

    # def get_image_preview(self, obj):
    #     if obj.image:
    #         return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
    #     return 'Нет изображения'
    # get_image_preview.short_description = 'Предпросмотр'


class DonorVehicleImageInline(admin.TabularInline):
    """
    Позволяет добавлять несколько изображений к конкретной машине-донору
    прямо на странице ее редактирования.
    """
    model = DonorVehicleImage
    extra = 1
    fields = ('image', 'is_main')


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
    list_display = ('part_id', 'title', 'price', 'donor_generation', 'compatible_auto_list', 'donor_vehicle', 'condition', 'is_active', 'created_at')
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


@admin.register(DonorVehicle)
class DonorVehicleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'generation', 'arrival_date', 'get_image_count')
    list_filter = ('generation__model__make', 'arrival_date')
    search_fields = ('title', 'generation__name')
    inlines = [DonorVehicleImageInline]    #Связываем инлайн-класс с основной моделью

    def get_image_count(self, obj):
        return obj.images.count()

    get_image_count.short_description = 'Фото'
