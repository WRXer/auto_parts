"""The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from users.apps import UsersConfig
from users.views import RegistrationView, ProfileView
from django.contrib.auth import views as auth_views

app_name = UsersConfig.name


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration_page'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password/change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change_form.html'), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
