from django.db import models
from django.utils import timezone

from core.models import GiftType


class DailyStats(models.Model):
    date = models.DateField(default=timezone.now)
    gift_type = models.ForeignKey(GiftType, on_delete=models.CASCADE, related_name="daily_stats")
    average_rate = models.FloatField()
    average_face_value = models.IntegerField()
    min_rate = models.FloatField()
    sold_num = models.IntegerField()
    sell_num = models.IntegerField()

    class Meta:
        unique_together = ("date", "gift_type")
