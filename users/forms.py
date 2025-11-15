from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',) + UserCreationForm.Meta.fields            #Таким образом, phone не будет показываться, и Django не будет пытаться его валидировать.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True    #Убеждаемся, что email всегда требуется, несмотря на настройки модели
        if 'phone' in self.fields:    #ИСКЛЮЧАЕМ ПОЛЕ PHONE из формы
            del self.fields['phone']
        if 'username' in self.fields:    #ИСКЛЮЧАЕМ ПОЛЕ USERNAME
            del self.fields['username']