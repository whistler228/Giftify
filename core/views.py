from django.shortcuts import render

from .models import GiftType


def top(request):
    gift_types = [f"images/gift_logo/{x}.png" for x in GiftType.objects.all().values_list("name", flat=True)]
    return render(request, "core/top.html", {"gift_types": gift_types})
