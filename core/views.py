from django.shortcuts import render, get_object_or_404

from .forms import GiftFormSearch
from .models import GiftType


def top(request):
    gift_types = [{"url": f"images/gift_logo/{x}.png", "name": x} for x in
                  GiftType.objects.all().values_list("name", flat=True)]

    return render(request, "core/top.html", {"gift_types": gift_types})


def plot(request, gift_type):
    gift_type = get_object_or_404(GiftType, name=gift_type)
    form = GiftFormSearch({"gift_type": gift_type.name, "available": 0})
    return render(request, "core/plot.html", {"form": form, "gift_type": gift_type.display_name})
