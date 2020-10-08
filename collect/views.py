import requests
from django.utils import timezone

from core.models import *


def collect_from_api(gift_type):
    api = "https://amaten.com/api/gifts"

    headers = {"X-Requested-With": "XMLHttpRequest"}
    params = {"order": "", "type": gift_type, "limit": 100, "last_id": ""}
    res = requests.get(api, headers=headers, params=params)

    gifts = res.json()["gifts"]
    gift_ids = [x["id"] for x in gifts]
    gift_type = GiftType.objects.get(name=gift_type)

    date = timezone.make_aware(timezone.datetime.now().replace(second=0, microsecond=0))

    Gift.objects.filter(gift_type__name=gift_type, available=True).exclude(gift_id__in=gift_ids).update(available=False,
                                                                                                        sold_at=date)

    for g in gifts:
        try:
            gift = Gift.objects.get(gift_id=g["id"])
        except Gift.DoesNotExist:
            gift = Gift.objects.create(
                gift_id=g["id"],
                gift_type=gift_type,
                face_value=g["face_value"],
                price=g["price"],
                rate=g["rate"],
                available=True,
                added_at=date
            )
    return True
