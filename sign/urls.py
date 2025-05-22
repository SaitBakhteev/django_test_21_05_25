from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, SignUpView

urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='sign/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='sign/logout.html'), name='logout'),
    path('signup/', SignUpView.as_view(template_name='sign/signup.html'), name='signup'),
]