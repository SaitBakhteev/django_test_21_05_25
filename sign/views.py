from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from .models import BaseRegister


class SignUpView(CreateView):
    model = User
    form_class = BaseRegister
    success_url = '/ads'


class CustomLoginView(LoginView):
    redirect_authenticated_user = True  # перенаправляем авторизованных пользователей
    success_url = '/ads'