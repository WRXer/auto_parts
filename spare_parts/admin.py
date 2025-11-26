import re
from django.db import transaction
from django.utils.safestring import mark_safe
from django.contrib import admin
from spare_parts.forms import DonorVehicleAdminForm, PartAdminForm
from spare_parts.models import Part, CarGeneration, CarMake, CarModel, PartImage, DonorVehicle, \
    DonorVehicleImage, Category, PartSubCategory


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
    list_display = ('name', 'slug')
    search_fields = ('name',)

    class Meta:
        model = Part
        fields = '__all__'

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    inlines = [PartImageInline]
    form = PartAdminForm
    list_display = ('title', 'price','category', 'is_active', 'get_main_image_preview', 'get_donor_vin')
    list_filter = ('is_active', 'condition','category', 'donor_generation__model__make')
    search_fields = ('title', 'part_number', 'part_id', 'description')
    filter_horizontal = ('car_generations',)

    def save_model(self, request, obj, form, change):
        """
        Сохраняет объект Part и обрабатывает пакетный ввод URL,
        создавая новые записи PartImage.
        """
        super().save_model(request, obj, form, change)

        bulk_urls = form.cleaned_data.get('bulk_url_input')
        if bulk_urls:
            urls = re.split(r'[,\s\t\n]+', bulk_urls)    #Разделяем текст по разделителям (запятые, пробелы, новая строка)
            valid_urls = [url.strip() for url in urls if url.strip().startswith('http')]
            is_main_exists = obj.images.filter(is_main=True).exists()

            with transaction.atomic():
                for index, url in enumerate(valid_urls):
                    make_main = False
                    if index == 0 and not is_main_exists:
                        make_main = True
                        is_main_exists = True    #Устанавливаем флаг
                    PartImage.objects.create(
                        part=obj,    #Ссылка на текущую запчасть
                        image_url=url,    #Сохраняем ссылку в поле URL
                        is_main=make_main
                    )

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

    def get_donor_vin(self, obj):
        """Возвращает поле donor_vin из связанного DonorVehicle."""
        if obj.donor_vehicle:
            return obj.donor_vehicle.donor_vin   #Получаем значение поля donor_vin из связанного донора
        return '—'    #Если донор не привязан
    get_donor_vin.short_description = 'Конкретная машина-донор(поступление)'


@admin.register(DonorVehicle)
class DonorVehicleAdmin(admin.ModelAdmin):
    form = DonorVehicleAdminForm  # Используем кастомную форму
    list_display = ('__str__', 'id', 'donor_vin', 'generation', 'get_main_image_preview', 'title', 'color', 'engine_details', 'description', 'transmission_type' ,'arrival_date', 'get_image_count')
    list_filter = ('generation__model__make', 'arrival_date')
    search_fields = ('title', 'generation__name')
    inlines = [DonorVehicleImageInline]    #Связываем инлайн-класс с основной моделью

    def save_model(self, request, obj, form, change):
        """
        Сохраняет объект DonorVehicle и обрабатывает пакетный ввод URL,
        создавая новые записи DonorVehicleImage.
        """

        # 1. Сначала сохраняем сам объект донора
        super().save_model(request, obj, form, change)

        # 2. Обрабатываем пакетный ввод
        bulk_urls = form.cleaned_data.get('bulk_url_input')

        if bulk_urls:
            # Разделяем текст по запятым, пробелам, переводам строки.
            # Фильтруем и убираем пустые строки, оставляем только те, что похожи на ссылки.
            urls = re.split(r'[,\s\t\n]+', bulk_urls)
            valid_urls = [url.strip() for url in urls if url.strip().startswith('http')]

            # Проверяем, есть ли уже главное фото
            is_main_exists = obj.images.filter(is_main=True).exists()

            # Создаем записи в базе данных
            with transaction.atomic():
                for index, url in enumerate(valid_urls):
                    # Если главный снимок еще не задан, делаем первый в пакете главным
                    make_main = False
                    if index == 0 and not is_main_exists:
                        make_main = True
                        is_main_exists = True  # Устанавливаем флаг, чтобы следующие фото не стали главными

                    DonorVehicleImage.objects.create(
                        donor_vehicle=obj,
                        image_url=url,  # Сохраняем ссылку сюда
                        is_main=make_main
                    )


    def get_image_count(self, obj):
        return obj.images.count()

    def get_main_image_preview(self, obj):
        url = obj.get_main_image_source()   #Используем метод из модели DonorVehicle
        if url:
            return mark_safe(f'<img src="{url}" style="max-height: 50px; max-width: 70px; border-radius: 4px;" />')
        return 'Нет фото'

    get_main_image_preview.short_description = 'Главное фото'
    get_image_count.short_description = 'Фото'


@admin.register(PartSubCategory)
class PartSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'slug')
    list_filter = ('category',)    #Отличный фильтр по главной категории
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}    #Автозаполнение ЧПУ из названия