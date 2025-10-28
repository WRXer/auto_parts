from django.contrib import admin

from spare_parts.models import Part, CarGeneration, CarMake, CarModel, Category


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

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'price', 'donor_generation', 'compatible_auto_list', 'condition', 'is_active', 'created_at'
    )
    filter_horizontal = ('car_generations',)

    def compatible_auto_list(self, obj):
        """
        Возвращает строку с названиями совместимых автомобилей.
        """
        full_list = []
        for gen in obj.car_generations.all():
            full_list.append(str(gen))
        return ", ".join(full_list)

    compatible_auto_list.short_description = 'Совместимые авто'  # Заголовок столбца

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)