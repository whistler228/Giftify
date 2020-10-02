import logging

from django.test import TestCase

from account.models import CustomUser
from core.models import GiftType, Gift
from .tasks import send

logger = logging.getLogger(__name__)


class SendMailTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SendMailTest, cls).setUpClass()
        cls.user = CustomUser.objects.create(username="test_user", email="kadonoboti1@gmail.com", password="1234")
        gift_type = GiftType.objects.create(name="google_play")
        cls.gift = Gift.objects.create(gift_id=1, face_value=10000, price=8200, rate=82.0, gift_type=gift_type,
                                       available=True)
        cls.gift = Gift.objects.create(gift_id=2, face_value=10000, price=8300, rate=83.0, gift_type=gift_type,
                                       available=True)

    def test_sendmail(self):
        r = send([self.gift.gift_id], self.user.username)
        return self.assertEqual(self.user.email, r)
