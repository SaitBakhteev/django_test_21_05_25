from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ads.models import Ad, ExchangeProposal
from ads.serializers import AdSerializer, ExchangeProposalSerializer
from django.contrib.auth.models import User


class AdListCreateView(generics.ListCreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'condition']
    search_fields = ['title', 'description']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            return Response({'error': 'Вы не являетесь автором этого объявления'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            return Response({'error': 'Вы не являетесь автором этого объявления'},
                            status=status.HTTP_403_FORBIDDEN)
        instance.delete()


class ExchangeProposalCreateView(generics.CreateAPIView):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        ad_receiver = get_object_or_404(Ad, id=self.request.data.get('ad_receiver'))

        # Проверка, что пользователь не отправляет предложение самому себе
        if ad_receiver.user == self.request.user:
            return Response({'error': 'Нельзя отправлять предложение самому себе'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Проверка, что у пользователя есть хотя бы одно объявление
        user_ads = Ad.objects.filter(user=self.request.user)
        if not user_ads.exists():
            return Response({'error': 'У вас нет объявлений для обмена'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Используем первое объявление пользователя как ad_sender
        serializer.save(ad_sender=user_ads.first(), ad_receiver=ad_receiver)


class ExchangeProposalListView(generics.ListAPIView):
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        user = self.request.user
        return ExchangeProposal.objects.filter(ad_sender__user=user) | \
            ExchangeProposal.objects.filter(ad_receiver__user=user)


class ExchangeProposalUpdateView(generics.UpdateAPIView):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def perform_update(self, serializer):
        proposal = self.get_object()

        # Проверяем, что пользователь является получателем предложения
        if proposal.ad_receiver.user != self.request.user:
            return Response({'error': 'Вы не можете изменять это предложение'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer.save()
# Create your views here.
