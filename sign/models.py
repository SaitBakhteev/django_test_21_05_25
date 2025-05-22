from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms


# Стандартная форма регистрации пользователей
class BaseRegister(UserCreationForm):
    email = forms.EmailField(label='Адрес электронной почты', required=True)
    first_name = forms.CharField(label='Имя', required=True)
    last_name = forms.CharField(label='Фамилия', required=True)
    username = forms.CharField(label='Username', required=True)

    class Meta:
        model = User
        fields = ("first_name",
                  "last_name",
                  "username",
                  "email",
                  "password1",
                  "password2", )
