from django.contrib.messages import get_messages
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.http import require_http_methods
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
            activation_link = f"https://{current_site.domain}/activate/{uid}/{token}/"

            email_context = {
                'user': user,
                'activation_link': activation_link,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            }

            html_message = render_to_string('users/email/activation_body.html', email_context)
            subject = render_to_string('users/email/activation_subject.txt', email_context).strip()

            try:
                send_mail(
                    subject,
                    'Пожалуйста, активируйте ваш аккаунт, перейдя по ссылке.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],    #Получатель
                    html_message=html_message,    #Отправляем HTML-версию
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Ошибка при отправке Email: {e}")
                messages.error(request, "Ошибка при отправке письма активации. Проверьте настройки почты.")

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
        all_orders = None
        all_users = None
        if user.is_superuser:
            all_orders = Order.objects.all().order_by('-created_timestamp').select_related('user').prefetch_related(
                'items')
            all_users = User.objects.all().order_by('id')
        context = {
            'user': user,
            'orders': orders,
            'all_orders': all_orders,
            'all_users': all_users,
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


@require_http_methods(["POST"])
def update_user_status(request, user_id):
    """
    Обрабатывает AJAX-запрос на изменение статуса активности пользователя.
    Требуется соответствующий URL-маршрут в users/urls.py.
    """
    if not request.user.is_superuser:    #Проверка прав администратора
        return JsonResponse({'success': False, 'error': 'Доступ запрещен'}, status=403)
    user_to_update = get_object_or_404(User, pk=user_id)

    if user_to_update.is_superuser:     #Защита от блокировки самого себя
        return JsonResponse({'success': False, 'error': 'Нельзя изменить статус суперпользователя.'}, status=400)
    is_active_str = request.POST.get('is_active')
    if is_active_str is None:
        return JsonResponse({'success': False, 'error': 'Неверные данные'}, status=400)

    new_status = is_active_str == 'True'
    user_to_update.is_active = new_status    #Обновление статуса
    user_to_update.save()
    return JsonResponse({'success': True, 'is_active': new_status})