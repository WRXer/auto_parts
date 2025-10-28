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
        'title', 'price', 'donor_generation', 'condition', 'is_active', 'created_at'
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)