import logging

from django.test import TestCase
from django.utils import timezone

from account.models import CustomUser, Condition
from core.models import GiftType, Gift
from .tasks import check_condition, send_mail

logger = logging.getLogger(__name__)


class SendMailTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SendMailTest, cls).setUpClass()
        cls.user = CustomUser.objects.create(username="test_user", email="kadonoboti1@gmail.com", password="1234")
        gift_type = GiftType.objects.create(name="google_play", display_name="Google Play Card")
        cls.gift = Gift.objects.create(gift_id=1, face_value=10000, price=8200, rate=82.0, gift_type=gift_type,
                                       available=True, added_at=timezone.now())
        cls.gift2 = Gift.objects.create(gift_id=2, face_value=10000, price=8300, rate=83.0, gift_type=gift_type,
                                        available=True, added_at=timezone.now())

    def test_sendmail(self):
        r = send_mail([self.gift.gift_id], self.gift.gift_type.name, 1234, self.user.username)
        return self.assertEqual(self.user.email, r)


class ConditionCheckTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ConditionCheckTest, cls).setUpClass()
        cls.user = CustomUser.objects.create(username="test_user", email="kadonoboti1@gmail.com", password="1234")
        gift_type = GiftType.objects.create(name="google_play")
        cls.gift1 = Gift.objects.create(gift_id=1, face_value=10000, price=8500, rate=85.0, gift_type=gift_type,
                                        available=True)
        cls.gift2 = Gift.objects.create(gift_id=2, face_value=10000, price=8200, rate=82.0, gift_type=gift_type,
                                        available=True)
        cls.gift3 = Gift.objects.create(gift_id=3, face_value=1000, price=850, rate=85.0, gift_type=gift_type,
                                        available=True)
        cls.condition1 = Condition.objects.create(gift_type=gift_type, min_price=5000, max_price=10000, max_rate=85.0)
        cls.condition2 = Condition.objects.create(gift_type=gift_type, max_price=10000, max_rate=85.0)
        cls.condition3 = Condition.objects.create(gift_type=gift_type)
        cls.user.condition.add(cls.condition1)
        cls.user.condition.add(cls.condition2)
        cls.user.condition.add(cls.condition3)

    def test_check_condition(self):
        for condition in self.user.condition.all():
            res = check_condition(condition)
            self.assertTrue(res)
