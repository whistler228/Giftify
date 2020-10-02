from django.db.utils import IntegrityError
from django.test import TestCase

from .models import CustomUser


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
