from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('email', 'phone', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'role', 'is_staff')

    fieldsets = (
        (None, {'fields': ('email', 'phone')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'role', 'image')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'first_name', 'last_name',  'role', 'is_staff', 'is_active'),
        }),
    )

    search_fields = ('email', 'phone', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')