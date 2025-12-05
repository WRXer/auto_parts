from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User

from phonenumber_field.phonenumber import PhoneNumber
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class EmailOrPhoneBackend(ModelBackend):
    """
    Позволяет аутентифицировать пользователя по email ИЛИ телефону.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return None
        is_email = False    #Определяем тип ввода (Email или Телефон)
        try:
            validate_email(username)
            is_email = True
        except ValidationError:
            pass

        try:
            if is_email:
                query = Q(email__iexact=username)
            else:
                phone_obj = PhoneNumber.from_string(username, region='RU')
                query = Q(phone=phone_obj)

            user = User.objects.get(query)
        except (User.DoesNotExist, Exception):
            return None
        if user.check_password(password):
            return user
        return None