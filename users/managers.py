from django.contrib.auth.models import (BaseUserManager)


class UserManager(BaseUserManager):
    """
    Менеджер для модели Юзера
    """
    def create_user(self, email, password=None, first_name="", last_name="", phone="", role='user', **extra_fields):
        """
        Функция создания пользователя — в нее мы передаем обязательные поля
        """
        if not email:
            raise ValueError('Email is required.')

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, phone=phone,role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, first_name='', last_name='', **extra_fields):
        """
        Функция для создания суперпользователя — с ее помощью мы создаем админинстратора
        это можно сделать с помощью команды createsuperuser
        """
        return self.create_user(email, password, first_name, last_name, role='admin', **extra_fields)