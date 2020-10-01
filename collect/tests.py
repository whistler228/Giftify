from django.test import TestCase

from core.models import GiftType, Gift
from . import views


class CollectDataTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(CollectDataTest, cls).setUpClass()
        cls.gift_type = GiftType.objects.create(name="google_play")

    def test(self):
        res = views.collect_from_api("google_play")
        print(Gift.objects.all())
        return self.assertTrue(len(res))
