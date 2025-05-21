from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ..models import Ad, ExchangeProposal
from ..forms import AdForm  # Создайте forms.py если еще нет
from django.db import models


class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # Добавьте здесь логику фильтрации, если нужно
        return queryset


class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_ads'] = Ad.objects.filter(user=self.request.user)
        return context


class AdCreateView(CreateView):
    model = Ad
    form_class = AdForm  # Или fields = ['title', 'description', ...]
    template_name = 'ads/ad_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ads:ad_detail', kwargs={'pk': self.object.pk})


class AdUpdateView(UpdateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'

    def get_success_url(self):
        return reverse_lazy('ads:ad_detail', kwargs={'pk': self.object.pk})


class AdDeleteView(DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'  # Создайте если нужно
    success_url = reverse_lazy('ads:ad_list')


class ProposalListView(ListView):
    model = ExchangeProposal
    template_name = 'ads/proposal_list.html'
    context_object_name = 'proposals'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Показываем только связанные с текущим пользователем предложения
        return queryset.filter(
            models.Q(ad_sender__user=self.request.user) |
            models.Q(ad_receiver__user=self.request.user)
        )


class ProposalCreateView(CreateView):
    model = ExchangeProposal
    fields = ['ad_receiver', 'comment']
    template_name = 'ads/proposal_form.html'  # Создайте если нужно

    def form_valid(self, form):
        form.instance.ad_sender = Ad.objects.get(
            id=self.request.POST.get('ad_sender'),
            user=self.request.user
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ads:proposal_list')


class ProposalUpdateView(UpdateView):
    model = ExchangeProposal
    fields = ['status']
    template_name = 'ads/proposal_update.html'  # Создайте если нужно

    def get_success_url(self):
        return reverse_lazy('ads:proposal_list')