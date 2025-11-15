from django.contrib import admin
from .forms import UserCreationForm
from .models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    add_form = UserCreationForm

    list_display = ('phone',
        'email',
        'first_name',
        'is_active',
        'is_staff',
    )

    fieldsets = (
        (None, {'fields': ('phone', 'email', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'role')}),
        ('Права доступа', {
            'fields': ('is_active', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'email', 'first_name', 'last_name', 'password', 'role'),
        }),
    )    #Поля, которые мы хотим видеть при создании:

    list_filter = ('is_active', 'role')
    search_fields = ('phone', 'email', 'first_name', 'last_name')
    ordering = ('phone',)