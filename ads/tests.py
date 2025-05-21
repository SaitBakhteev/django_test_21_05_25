from django.test import TestCase
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal


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

# Create your tests here.
