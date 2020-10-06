from django.shortcuts import render

from .models import GiftType, Gift


def top(request):
    gift_types = [{"url": f"images/gift_logo/{x}.png", "name": x} for x in
                  GiftType.objects.all().values_list("name", flat=True)]

    return render(request, "core/top.html", {"gift_types": gift_types})


def plot(request, gift_type):
    gifts = Gift.objects.filter(gift_type__name=gift_type)
    labels = [f"{x.face_value}" for x in gifts]
    return render(request, "core/plot.html", {"gifts": gifts, "labels": labels})
