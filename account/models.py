from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import Gift, GiftType


class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=12)
    notified = models.ManyToManyField(Gift, related_name="notified_users")
    email = models.EmailField(blank=True, unique=True)
    is_send_mail = models.BooleanField(default=True)
    timezone = models.TextField(max_length=32, default="Asia/Tokyo")


class Condition(models.Model):
    user = models.ManyToManyField("CustomUser", related_name="condition")
    gift_type = models.ForeignKey(GiftType, on_delete=models.CASCADE, related_name="cond_gift_type")
    min_price = models.IntegerField(null=True)
    max_price = models.IntegerField(null=True)
    max_rate = models.IntegerField(null=True)

    class Meta:
        unique_together = ["gift_type", "min_price", "max_price", "max_rate"]

    def __str__(self):
        return f"{self.gift_type.name}:{self.min_price}~{self.max_price}:{self.max_rate}"
