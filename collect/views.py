import requests

from core.models import *


def collect_from_api(gift_type):
    api = "https://amaten.com/api/gifts"

    headers = {"X-Requested-With": "XMLHttpRequest"}
    params = {"order": "", "type": gift_type, "limit": 100, "last_id": ""}
    res = requests.get(api, headers=headers, params=params)

    gifts = res.json()["gifts"]
    gift_type = GiftType.objects.get(name=gift_type)

    Gift.objects.filter(available=True).update(available=False)
    for g in gifts:
        gift, _ = Gift.objects.update_or_create(
            gift_id=g["id"],
            defaults={
                "gift_type": gift_type,
                "face_value": g["face_value"],
                "price": g["price"],
                "rate": g["rate"],
                "available": True}
        )
    return True
