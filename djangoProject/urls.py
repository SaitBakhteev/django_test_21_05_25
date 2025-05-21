from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

schema_view = get_schema_view(title='API of change platform')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ads.urls')),
    path('api/docs/', include_docs_urls(title='API Docs')),
    path('api/schema/', schema_view),
]