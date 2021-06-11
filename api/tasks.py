from datetime import timedelta

from django.db.models import Avg, Min
from django.utils import timezone
from huey import crontab
from huey.contrib.djhuey import periodic_task

from core.models import Gift, GiftType
from .models import DailyStats


@periodic_task(crontab(day="*/1", hour="0", minute="5"))
def periodic_daily_stats():
    for gift_type in GiftType.objects.all():
        date = timezone.now() - timedelta(days=1)
        gifts = Gift.objects.filter(gift_type=gift_type, added_at__gte=date.date())
        if gifts:
            stats = gifts.aggregate(Avg("rate"), Min("rate"), Avg("face_value"))
            ds, _ = DailyStats.objects.get_or_create(gift_type=gift_type, date=date, defaults={
                "average_rate": stats["rate__avg"],
                "average_face_value": stats["face_value__avg"],
                "min_rate": stats["rate__min"],
                "sold_num": gifts.filter(available=False).count(),
                "sell_num": gifts.count(),
            })
