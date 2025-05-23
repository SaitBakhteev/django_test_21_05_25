from django.db import models
from django_filters import FilterSet, CharFilter, ChoiceFilter
from .models import Ad

class AdFilter(FilterSet):
    # Поиск по ключевым словам в заголовке и описании
    search = CharFilter(method='filter_search',label='Поиск')

    # Фильтрация по категории и состоянию
    category = ChoiceFilter(choices=Ad.CATEGORY_CHOICES,label='Категория')
    condition = ChoiceFilter(choices=Ad.CONDITION_CHOICES,label='Состояние')

    class Meta:
        model = Ad
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(description__icontains=value)
        )