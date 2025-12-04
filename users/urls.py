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
from django.urls import path, reverse_lazy
from users.apps import UsersConfig
from users.views import RegistrationView, ProfileView, ActivateView, ProfileEditView, update_user_status, \
    update_catalog_view
from django.contrib.auth import views as auth_views

app_name = UsersConfig.name


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration_page'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('password/change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change_form.html', success_url=reverse_lazy('users:password_change_done')), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
    path('password/reset/',auth_views.PasswordResetView.as_view(template_name='users/password_reset_form.html',
                                                                subject_template_name='users/email/password_reset_subject.txt',
                                                                email_template_name='users/email/password_reset_body.txt',
                                                                html_email_template_name='users/email/password_reset_body.html',
                                                                success_url=reverse_lazy('users:password_reset_done')
                                                                ),name='password_reset'),
    path('password/reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                                                               success_url=reverse_lazy('users:password_reset_complete')),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),name='password_reset_complete'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('update_user_status/<int:user_id>/', update_user_status, name='update_user_status'),
    path('activate/<str:uidb64>/<str:token>/', ActivateView.as_view(), name='activate'),

    path('profile/update-catalog/', update_catalog_view, name='update_catalog'),

]
