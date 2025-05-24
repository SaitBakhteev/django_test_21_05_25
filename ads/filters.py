from random import choices

from django.db.models import Q, functions
from django_filters import FilterSet, CharFilter, ChoiceFilter
from .models import Ad, ExchangeProposal

class AdFilter(FilterSet):
    # Поиск по ключевым словам в заголовке и описании
    search = CharFilter(method='filter_search', label='Поиск', )

    # Фильтрация по категории и состоянию
    category = ChoiceFilter(choices=Ad.CATEGORY_CHOICES,label='Категория')
    condition = ChoiceFilter(choices=Ad.CONDITION_CHOICES,label='Состояние')

    # Метод, позволяющий искать либо в названии, либо в описании
    def filter_search(self, queryset, name, value):
        search_value = value.lower() if value else ''
        return queryset.filter(
            Q(title__icontains=search_value) |
            Q(description__icontains=search_value)
        )

    class Meta:
        model = Ad
        fields = []


class ExchangeProposalFilter(FilterSet):
    ad_sender = CharFilter(method='sender_search', label='Инициатор предложения', )
    ad_receiver = CharFilter(method='receiver_search', label='Получатель предложения', )
    status = ChoiceFilter(choices=ExchangeProposal.STATUS_CHOICES, label='Статус')

    # Метод для поиска по логину, имени, фамилии или почте инициатора обмена
    def sender_search(self, queryset, name, value):
        search_value = value.lower() if value else ''
        return queryset.filter(
            Q(ad_sender__user__username__icontains=search_value) |
            Q(ad_sender__user__first_name__icontains=search_value) |
            Q(ad_sender__user__last_name__icontains=search_value) |
            Q(ad_sender__user__email__icontains=search_value)
        )

    # Метод для поиска по логину, имени, фамилии или почте инициатора обмена
    def receiver_search(self, queryset, name, value):
        search_value = value.lower() if value else ''
        return queryset.filter(
            Q(ad_receiver__user__username__icontains=search_value) |
            Q(ad_receiver__user__first_name__icontains=search_value) |
            Q(ad_receiver__user__last_name__icontains=search_value) |
            Q(ad_receiver__user__email__icontains=search_value)
        )

    class Meta:
        model = ExchangeProposal
        fields = []