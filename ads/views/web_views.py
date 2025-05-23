from django.contrib import messages
from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView,
                                  DeleteView, TemplateView)
from django.urls import reverse_lazy
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django_filters.views import FilterView

from ..models import Ad, ExchangeProposal
from ..forms import AdForm
from ..filters import AdFilter

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
        return queryset


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('main-page')
    success_message = "Объявление успешно создано!"

    def form_valid(self, form):
        messages.success(self.request, "Объявление успешно создано!")
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # Перенаправляем на главную с параметром для показа модального окна
        return reverse_lazy('main-page') + '?show_success=1'

class AdUpdateView(UpdateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'

    def get_success_url(self):
        return reverse_lazy('main-page')


class AdDeleteView(DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('main-page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context


class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_ads'] = Ad.objects.filter(user=self.request.user)
        return context


class ProposalListView(ListView):
    model = ExchangeProposal
    template_name = 'ads/proposal_list.html'
    context_object_name = 'proposals'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Показывать только связанные с текущим пользователем предложения
        return queryset.filter(
            models.Q(ad_sender__user=self.request.user) |
            models.Q(ad_receiver__user=self.request.user)
        )


class ProposalCreateView(CreateView):
    model = ExchangeProposal
    fields = ['ad_receiver', 'comment']
    template_name = 'ads/proposal_form.html'

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
    template_name = 'ads/proposal_update.html'

    def get_success_url(self):
        return reverse_lazy('proposal_list')
