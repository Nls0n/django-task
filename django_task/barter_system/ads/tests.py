from django.test import TestCase
from django.contrib.auth.models import User
from models import Ad, ExchangeProposal


class AdModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.ad = Ad.objects.create(
            user=cls.user,
            title="Test Item",
            description="Test Description",
            category="electronics",
            condition="new"
        )

    def test_ad_creation(self):
        self.assertEqual(self.ad.status, 'active')
        self.assertEqual(str(self.ad), "Test Item")


class ExchangeProposalTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1')
        self.user2 = User.objects.create_user(username='user2')

        self.ad1 = Ad.objects.create(user=self.user1, title="Ad 1")
        self.ad2 = Ad.objects.create(user=self.user2, title="Ad 2")

        self.proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment="Test proposal"
        )

    def test_proposal_status_default(self):
        self.assertEqual(self.proposal.status, 'pending')
