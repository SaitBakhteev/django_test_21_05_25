from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Ad(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Электроника'),
        ('clothing', 'Одежда'),
        ('books', 'Книги'),
        ('home', 'Для дома'),
        ('other', 'Другое'),
    ]

    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/у'),
        ('broken', 'Требует ремонта'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    # Инициатор предложения предлагает этот товар
    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='sent_proposals')

    # Это товар получателя предложения, на которое просит обменять инициатор
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='received_proposals')

    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Предложение от {self.ad_sender.user.username} к {self.ad_receiver.user.username}"
