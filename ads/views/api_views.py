from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, filters
from rest_framework.request import Request
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ads.models import Ad, ExchangeProposal
from ads.serializers import AdSerializer, ExchangeProposalSerializer
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
    extend_schema_view,
)

@extend_schema_view(
    get=extend_schema(
        summary="Получить список объявлений",
        description="Возвращает список всех объявлений с возможностью фильтрации и поиска",
        parameters=[
            OpenApiParameter(name='category', description='Фильтр по категории', required=False, type=str),
            OpenApiParameter(name='condition', description='Фильтр по состоянию', required=False, type=str),
            OpenApiParameter(name='search', description='Поиск по названию и описанию', required=False, type=str),
        ],
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                value=[
                    {
                        "id": 1,
                        "title": "Книга по Python",
                        "description": "Новая книга",
                        "category": "books",
                        "condition": "new"
                    }
                ],
                response_only=True,
                status_codes=['200']
            )
        ]
    ),
    post=extend_schema(
        summary="Создать новое объявление",
        description="Создает новое объявление для текущего пользователя",
        request=AdSerializer,
        responses={
            201: OpenApiResponse(description="Объявление успешно создано"),
            400: OpenApiResponse(description="Неверные данные"),
            403: OpenApiResponse(description="Недостаточно прав")
        }
    )
)
class AdListCreateView(generics.ListCreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'condition']
    search_fields = ['title', 'description']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary="Получить детали объявления",
        description="Возвращает полную информацию об объявлении"
    ),
    put=extend_schema(
        summary="Обновить объявление",
        description="Полностью обновляет информацию об объявлении",
        request=AdSerializer,
        responses={
            403: OpenApiResponse(description="Недостаточно прав (не автор объявления)")
        }
    ),
    patch=extend_schema(
        summary="Частично обновить объявление",
        description="Обновляет отдельные поля объявления",
        request=AdSerializer
    ),
    delete=extend_schema(
        summary="Удалить объявление",
        description="Удаляет объявление",
        responses={
            204: OpenApiResponse(description="Объявление удалено"),
            403: OpenApiResponse(description="Недостаточно прав (не автор объявления)")
        }
    )
)
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


@extend_schema_view(
    post=extend_schema(
        summary="Создать предложение обмена",
        description="Создает новое предложение обмена между объявлениями",
        request=ExchangeProposalSerializer,
        responses={
            201: OpenApiResponse(description="Предложение создано"),
            400: OpenApiResponse(description="Неверные данные (нет объявлений для обмена или попытка обмена с собой)"),
            403: OpenApiResponse(description="Недостаточно прав")
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "ad_receiver": 1,
                    "comment": "Предлагаю обмен на мою книгу"
                },
                request_only=True
            )
        ]
    )
)
class ExchangeProposalCreateView(generics.CreateAPIView):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):

        # Убедитесь, что self.request имеет правильный тип
        if not isinstance(self.request, Request):
            raise ValueError("Expected DRF Request object")

        ad_receiver_id = self.request.data.get('ad_receiver')
        if not ad_receiver_id:
            raise ValueError("ad_receiver is required")

        ad_receiver = get_object_or_404(Ad, id=ad_receiver_id)


        if ad_receiver.user == self.request.user:
            return Response({'error': 'Нельзя отправлять предложение самому себе'},
                          status=status.HTTP_400_BAD_REQUEST)

        user_ads = Ad.objects.filter(user=self.request.user)
        if not user_ads.exists():
            return Response({'error': 'У вас нет объявлений для обмена'},
                          status=status.HTTP_400_BAD_REQUEST)

        serializer.save(ad_sender=user_ads.first(), ad_receiver=ad_receiver)


@extend_schema_view(
    get=extend_schema(
        summary="Получить список предложений",
        description="Возвращает список предложений обмена, связанных с текущим пользователем",
        parameters=[
            OpenApiParameter(name='status', description='Фильтр по статусу', required=False, type=str, enum=['pending', 'accepted', 'rejected'])
        ]
    )
)
class ExchangeProposalListView(generics.ListAPIView):
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self) -> QuerySet[ExchangeProposal]:
        user = self.request.user
        sender_qs = ExchangeProposal.objects.filter(ad_sender__user=user)
        receiver_qs = ExchangeProposal.objects.filter(ad_receiver__user=user)
        return sender_qs.union(receiver_qs)


@extend_schema_view(
    patch=extend_schema(
        summary="Обновить статус предложения",
        description="Обновляет статус предложения обмена (только для получателя)",
        request=ExchangeProposalSerializer,
        responses={
            200: OpenApiResponse(description="Статус обновлен"),
            403: OpenApiResponse(description="Недостаточно прав (не получатель предложения)")
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={"status": "accepted"},
                request_only=True
            )
        ]
    )
)
class ExchangeProposalUpdateView(generics.UpdateAPIView):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def perform_update(self, serializer):
        proposal = self.get_object()
        if proposal.ad_receiver.user != self.request.user:
            return Response({'error': 'Вы не можете изменять это предложение'},
                          status=status.HTTP_403_FORBIDDEN)
        serializer.save()