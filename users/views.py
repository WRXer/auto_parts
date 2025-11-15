from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.conf import settings


class RegistrationView(View):
    """
    Регистрация
    """
    def get(self, request):
        form = CustomUserCreationForm()
        context = {
            'form': form
        }
        return render(request, 'users/registration.html', context)

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend_path = settings.AUTHENTICATION_BACKENDS[0]    #Берем путь к бэкенду из настроек (первый в списке)
            login(request, user, backend=backend_path)
            messages.success(request, f"Аккаунт {user.email} успешно зарегистрирован!")
            return redirect('/')
        context = {
            'form': form
        }
        return render(request, 'users/registration.html', context)


class ProfileView(View):
    """
    Профиль
    """
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('users:login')

        context = {
            'user': request.user,
            'title': 'Мой профиль'
        }
        return render(request, 'users/profile.html', context)