from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


NULLABLE = {'blank': True, 'null': True}



class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Модель пользователя
    """
    ROLE_CHOICES = (
        ('user', 'пользователь'),
        ('admin', 'администратор'),
    )

    username = None
    first_name = models.CharField(max_length=25, verbose_name='Имя', **NULLABLE)
    last_name = models.CharField(max_length=255, verbose_name='Фамилия', **NULLABLE)
    phone = PhoneNumberField(unique=True,null=True,blank=True,region='RU', verbose_name='Номер телефона')
    email = models.EmailField(blank=True, null=True, unique=True, verbose_name='Емейл')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='роль пользователя')
    image = models.ImageField(upload_to='users/', verbose_name='аватар', **NULLABLE)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()  # <-- привязываем менеджер

    def __str__(self):
        return self.email or self.phone or f'User ID: {self.pk}'

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = 'пользователи'