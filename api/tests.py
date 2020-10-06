from django.test import TestCase
from django.urls import reverse

from account.models import CustomUser, Condition
from core.models import GiftType, Gift


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
        with self.subTest("Return true status"):
            self.assertTrue(res.status_code in [200, 302])

        with self.subTest("User's is_send_mail should be False"):
            self.assertFalse(self.user.is_send_mail)


class GetGiftTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(GetGiftTest, cls).setUpClass()
        gift_type = GiftType.objects.create(name="test")
        cls.gift1 = Gift.objects.create(gift_id=1, gift_type=gift_type, face_value=10000, price=9000, rate=90.,
                                        available=True)

    def test_get_data(self):
        res = self.client.get(reverse("api:get_gift"), {"type": "test"})
        print(res.json())
        return self.assertTrue(res.json()["status"])
