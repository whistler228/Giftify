from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import Gift, GiftType


class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=12)
    notified = models.ManyToManyField(Gift, related_name="notified_users")
    email = models.EmailField(blank=True, unique=True)


class Condition(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="condition")
    gift_type = models.ForeignKey(GiftType, on_delete=models.CASCADE, related_name="cond_gift_type")
    min_price = models.IntegerField(null=True)
    max_price = models.IntegerField(null=True)
    max_rate = models.IntegerField(null=True)
