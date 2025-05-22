from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ads/', include('ads.urls'), name='ads'),
    path('sign/', include('sign.urls'), name='sign'),

    # Авторизация
    path('accounts/', include('sign.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Стандартные URL аутентификации

    # Документация Spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]