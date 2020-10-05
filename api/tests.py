from django.test import TestCase
from django.urls import reverse

from account.models import CustomUser, Condition
from core.models import GiftType


class UnsubscriptionTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(UnsubscriptionTest, cls).setUpClass()
        cls.user = CustomUser.objects.create(username="test_user", email="test@test.com", password="1234")
        gift_type = GiftType.objects.create(name="test")
        cls.condition = Condition.objects.create(gift_type=gift_type, min_price=1000, max_price=10000, max_rate=85.)
        cls.user.condition.add(cls.condition)

    def test_unsubscribe(self):
        res = self.client.post(reverse("api:unsubscribe"),
                               data={"username": self.user.username, "email": self.user.email})
        self.user.refresh_from_db()
        data = res.json()
        with self.subTest("Return true status"):
            self.assertTrue(data["status"])

        with self.subTest("User's is_send_mail should be False"):
            self.assertFalse(self.user.is_send_mail)
