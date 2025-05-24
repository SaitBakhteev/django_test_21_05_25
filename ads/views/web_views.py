from django.contrib import messages
from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView,
                                  DeleteView, TemplateView)
from django.urls import reverse_lazy
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django_filters.views import FilterView
from rest_framework.exceptions import PermissionDenied

from ..models import Ad, ExchangeProposal
from ..forms import AdForm
from ..filters import AdFilter, ExchangeProposalFilter

# Загрузка главной страницы
class LandingView(LoginRequiredMixin, TemplateView):
    template_name = 'ads/main_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_success_modal'] = self.request.GET.get('show_success') == '1'
        return context


@login_required
def index(request):
    return render(request, 'ads/main_page.html')


class AdListView(LoginRequiredMixin, FilterView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10
    filterset_class = AdFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_at')


class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_ads'] = Ad.objects.filter(user=self.request.user)
        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ad-list')

    def form_valid(self, form):
        messages.success(self.request, "Объявление успешно создано!")
        form.instance.user = self.request.user
        return super().form_valid(form)


class AdUpdateView(UpdateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'

    # Чтобы сторонний пользователь не мог редактировать чужое объявление
    def dispatch(self, request, *args, **kwargs):
        # Получаем объект объявления
        self.object = self.get_object()

        try:
            # Проверяем, что текущий пользователь - владелец объявления
            if self.object.user != request.user:
                raise PermissionDenied("Вы не можете редактировать это объявление")

            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return redirect('error')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Тогда кнопка "Создать"  переименуется в ""Редактировать"
        context['is_update'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('main-page')


class AdDeleteView(DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('main-page')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            if self.object.user != request.user:
                raise PermissionDenied('У Вас нет прав на выполнение данного действия')
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return redirect('error')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context


class ProposalListView(ListView):
    model = ExchangeProposal
    template_name = 'ads/proposal_list.html'
    context_object_name = 'proposals'
    filterset_class = ExchangeProposalFilter

    def get_queryset(self):
        print(f'user_id={self.request.user.id}')

        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)

        # Применяем фильтры
        queryset = self.filterset.qs

        # Фильтрация по статусу (если нужна)
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Показывать только связанные с текущим пользователем предложения
        return queryset.filter(
            models.Q(ad_sender__user=self.request.user) |
            models.Q(ad_receiver__user=self.request.user)
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset  # Добавляем фильтр в контекст
        return context

class ProposalCreateView(CreateView):
    model = ExchangeProposal
    fields = ['ad_receiver', 'comment']

    def form_valid(self, form):
        form.instance.ad_sender = Ad.objects.get(
            id=self.request.POST.get('ad_sender'),
            user=self.request.user
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ad-list')


class ProposalUpdateView(UpdateView):
    model = ExchangeProposal
    fields = ['status']
    # template_name = 'ads/proposal_update.html'

    def get_success_url(self):
        return reverse_lazy('proposal-list')


# View для исключений
class PermissionDeniedView(TemplateView):
    template_name = 'errors.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error_message'] = "У вас нет прав для выполнения этого действия"
        return context
