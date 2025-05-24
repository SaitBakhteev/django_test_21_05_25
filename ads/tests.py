import pytest

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.management import call_command
from rest_framework.test import APIClient, APITestCase

from .models import Ad, ExchangeProposal


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('makemigrations', 'ads')  # Создаём миграции (если их нет)
        call_command('migrate', 'ads')         # Применяем ТОЛЬКО миграции ads


class AdModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username='testuser', password='12345')
        Ad.objects.create(
            user=test_user,
            title='Test Ad',
            description='Test Description',
            category='electronics',
            condition='new'
        )

    def test_ad_creation(self):
        ad = Ad.objects.get(id=1)
        self.assertEqual(ad.title, 'Test Ad')
        self.assertEqual(ad.user.username, 'testuser')


class ExchangeProposalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(username='user1', password='12345')
        user2 = User.objects.create_user(username='user2', password='12345')

        ad1 = Ad.objects.create(
            user=user1,
            title='Ad 1',
            description='Desc 1',
            category='electronics',
            condition='new'
        )

        ad2 = Ad.objects.create(
            user=user2,
            title='Ad 2',
            description='Desc 2',
            category='clothing',
            condition='used'
        )

        ExchangeProposal.objects.create(
            ad_sender=ad1,
            ad_receiver=ad2,
            comment='Test comment'
        )

    def test_proposal_creation(self):
        proposal = ExchangeProposal.objects.get(id=1)
        self.assertEqual(proposal.ad_sender.user.username, 'user1')
        self.assertEqual(proposal.ad_receiver.user.username, 'user2')
        self.assertEqual(proposal.status, 'pending')


# Функциональное тестирование API по работе с объявлениями

class AdAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = APIClient()
        self.client.force_login(user=self.user)  # Авторизация

    def test_create_ad(self):
        url = reverse('api-ad-list')
        data = {
            'title': 'New Ad',
            'description': 'Functional test',
            'category': 'electronics',
            'condition': 'new'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)  # Проверяем успешное создание
        self.assertEqual(Ad.objects.count(), 1)  # Проверяем, что объявление появилось в БД


class AdDetailAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.ad = Ad.objects.create(  # Создаём объявление для теста
            user=self.user,
            title='Test Ad',
            description='Test',
            category='electronics',
            condition='new'
        )
        self.client = APIClient()
        self.client.force_login(user=self.user)

    def test_retrieve_ad(self):
        url = reverse('api-ad-detail', kwargs={'pk': self.ad.pk})  # Передаём pk
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Test Ad')

    def test_update_ad(self):
        url = reverse('api-ad-detail', kwargs={'pk': self.ad.pk})
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Updated Title')

    def test_delete_ad(self):
        url = reverse('api-ad-detail', kwargs={'pk': self.ad.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Ad.objects.count(), 0)