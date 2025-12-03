from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'phone', 'first_name', 'last_name')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')

        if not email:    #Если email пустой, ошибка уже должна быть в поле email, но проверим.
            self.add_error('email', 'Email является обязательным полем для регистрации.')

        # АЛЬТЕРНАТИВНУЮ регистрация через телефон,
        # if not email and not phone:
        #     raise forms.ValidationError(
        #         "Для регистрации необходимо указать либо Email, либо Номер телефона."
        #     )

        for field in self.fields:
            if self.fields[field].widget.__class__.__name__ not in ('CheckboxInput', 'ClearableFileInput'):
                self.fields[field].widget.attrs['class'] = 'form-control'
        return cleaned_data


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('phone', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если поле 'password' присутствует в self.fields, удаляем его
        if 'password' in self.fields:
            del self.fields['password']