import re

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from users.managers import UserManager


NULLABLE = {'blank': True, 'null': True}

class User(AbstractUser):
    """
       Модель пользователя
       """
    ROLE_CHOICES = (
        ('user', 'пользователь'),
        ('admin', 'администратор'),
    )

    first_name = models.CharField(max_length=25, verbose_name='имя', **NULLABLE)
    last_name = models.CharField(max_length=255, verbose_name='фамилия', **NULLABLE)
    phone = PhoneNumberField(verbose_name='номер телефона', region='RU', blank=True, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='роль пользователя')
    image = models.ImageField(upload_to='users/', verbose_name='аватар', **NULLABLE)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # менеджер объектов
    objects = UserManager()


    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = 'пользователи'