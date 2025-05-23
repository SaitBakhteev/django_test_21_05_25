from django.urls import path
from .views import web_views, api_views


urlpatterns = [
    path('', web_views.LandingView.as_view(), name='main-page'),
    path('list/', web_views.AdListView.as_view(), name='ad-list'),
    path('create/', web_views.AdCreateView.as_view(), name='ad-create'),
    path('<int:pk>/', web_views.AdDetailView.as_view(), name='ad-detail'),
    path('<int:pk>/update/', web_views.AdUpdateView.as_view(), name='ad-update'),
    path('<int:pk>/delete/', web_views.AdDeleteView.as_view(), name='ad-delete'),

    # urls по предложениям
    path('proposals/', web_views.ProposalCreateView.as_view(), name='proposal-create'),
    path('proposals/list/', web_views.ProposalListView.as_view(), name='proposal-list'),
    path('proposals/<int:pk>/', web_views.ProposalUpdateView.as_view(), name='proposal-update'),

    # API Endpoints
    path('api/ads/', api_views.AdListCreateView.as_view(), name='api-ad-list'),
    path('api/ads/<int:pk>/', api_views.AdRetrieveUpdateDestroyView.as_view(), name='api-ad-detail'),
    path('api/proposals/', api_views.ExchangeProposalCreateView.as_view(), name='api-proposal-create'),
    path('api/proposals/list/', api_views.ExchangeProposalListView.as_view(), name='api-proposal-list'),
    path('api/proposals/<int:pk>/', api_views.ExchangeProposalUpdateView.as_view(), name='api-proposal-update'),

]