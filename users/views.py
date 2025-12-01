from django.contrib.messages import get_messages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from django.contrib import messages
from config import settings
from orders.models import Order
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User


class RegistrationView(View):
    """
    Регистрация
    """
    def get(self, request):
        storage = get_messages(request)
        storage.used = True

        form = CustomUserCreationForm()
        context = {
            'form': form
        }
        return render(request, 'users/registration.html', context)

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        context = {
            'form': form
        }
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False    #Деактивация аккаунта пока не подтвердили акк
            user.save()

            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))   #Кодируем ID пользователя (primary key)
            token = default_token_generator.make_token(user)    #Создаем токен (уникальный для этого пользователя и момента)
            activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"

            """ВЫВОД ССЫЛКИ В ТЕРМИНАЛ (вместо отправки Email)"""
            print("-" * 50)
            print(f"📧 Ссылка активации для пользователя {user.email}:")
            print(activation_link)
            print("-" * 50)

            context = {
                'registration_successful': True,    #Флаг для JS
                'user_email': user.email
            }
            return render(request, 'users/registration.html', context)
        return render(request, 'users/registration.html', context)


class ProfileView(View):
    """
    Профиль
    """
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('users:login')

        user = request.user
        user_email = user.email
        orders = Order.objects.filter(
            Q(user=user) | Q(email=user_email)
        ).distinct().order_by('-created_timestamp')
        context = {
            'user': user,
            'orders': orders,
            'title': 'Мой профиль'
        }
        return render(request, 'users/profile.html', context)


class ProfileEditView(View):
    """
    Профиль Редактирование данных.
    """
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('users:login')

        user = request.user
        form = CustomUserChangeForm(instance=user)
        context = {
            'user': user,
            'form': form,
            'title': 'Редактирование профиля'
        }
        return render(request, 'users/profile_edit.html', context)  # ❗ Новый шаблон!

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('users:login')

        user = request.user
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Данные профиля успешно обновлены!')
            return redirect('users:profile')    #Перенаправляем обратно на просмотр

        messages.error(request, 'Пожалуйста, проверьте ошибки в форме.')
        context = {
            'user': user,
            'form': form,
            'title': 'Редактирование профиля'
        }
        return render(request, 'users/profile_edit.html', context)

class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            # Декодируем ID пользователя
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Проверяем, существует ли пользователь и валиден ли токен
        if user is not None and default_token_generator.check_token(user, token):

            # 🔑 АКТИВАЦИЯ ПОЛЬЗОВАТЕЛЯ
            user.is_active = True
            user.save()

            # Автоматический вход после активации (опционально)
            backend_path = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user, backend=backend_path)

            messages.success(request, 'Ваш аккаунт успешно активирован!')
            return redirect('/')
        else:
            # Если токен невалиден или просрочен
            messages.error(request, 'Ссылка активации недействительна или устарела.')
            return redirect('users:registration')  # Или на страницу с ошибкой