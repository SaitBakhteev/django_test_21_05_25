from django.urls import path
from .views import api_views

urlpatterns = [
    path('ads/', api_views.AdListCreateView.as_view(), name='ad-list-create'),
    path('ads/<int:pk>/', api_views.AdRetrieveUpdateDestroyView.as_view(), name='ad-detail'),
    path('proposals/', api_views.ExchangeProposalCreateView.as_view(), name='proposal-create'),
    path('proposals/list/', api_views.ExchangeProposalListView.as_view(), name='proposal-list'),
    path('proposals/<int:pk>/', api_views.ExchangeProposalUpdateView.as_view(), name='proposal-update'),
]