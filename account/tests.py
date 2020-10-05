from django.db.utils import IntegrityError
from django.test import TestCase

from core.models import GiftType
from .models import CustomUser, Condition


class UserGetTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(UserGetTest, cls).setUpClass()
        cls.user = CustomUser.objects.create_user(username="test_user", email="test@test.com", password="test")

    def test_create_same_email(self):
        try:
            user2 = CustomUser.objects.create_user(username="test_user2", email="test@test.com", password="test")
        except IntegrityError:
            return True
        return False

    def test_get_user_by_username_email(self):
        user = CustomUser.objects.get(username="test_user", email="test@test.com")
        return self.assertEqual(user, self.user)

    def test_get_user_by_username_email2(self):
        user = CustomUser.objects.get(email="test@test.com")
        return self.assertEqual(user, self.user)


class ConditionTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ConditionTest, cls).setUpClass()
        cls.gift_type = GiftType.objects.create(name="test gift")

    def test_create_same1(self):
        condition1 = Condition.objects.create(gift_type=self.gift_type, min_price=5000, max_price=10000, max_rate=85)
        try:
            condition2 = Condition.objects.create(gift_type=self.gift_type, min_price=5000, max_price=10000,
                                                  max_rate=85)
        except IntegrityError:
            return True

    def test_create_same2(self):
        condition1 = Condition.objects.create(gift_type=self.gift_type)
        try:
            condition2 = Condition.objects.create(gift_type=self.gift_type)
        except IntegrityError:
            return True
