from django.urls import path
from .views import web_views

urlpatterns = [
    path('', web_views.LandingView.as_view(), name='main-page'),
    path('list/', web_views.AdListView.as_view(), name='ad-list'),
    path('create/', web_views.AdCreateView.as_view(), name='ad-create'),
    path('<int:pk>/update/', web_views.AdUpdateView.as_view(), name='ad-update'),
    path('<int:pk>/delete/', web_views.AdDetailView.as_view(), name='ad-delete'),
    path('<int:pk>/', web_views.AdDetailView.as_view(), name='ad-detail'),
    path('proposals/', web_views.ProposalCreateView.as_view(), name='proposal-create'),
    path('proposals/list/', web_views.ProposalListView.as_view(), name='proposal-list'),
    path('proposals/<int:pk>/', web_views.ProposalUpdateView.as_view(), name='proposal-update'),
]