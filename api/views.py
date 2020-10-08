from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

from account.models import CustomUser
from core.forms import GiftFormSearch
from core.models import Gift


# TODO: Conditionごとに配信設定できるように
def unsubscribe(request):
    if request.method != "POST":
        return JsonResponse({"status": False})

    email = request.POST.get("email")
    username = request.POST.get("username")
    if not email or not username:
        messages.error(request, "Please enter username and email.")
        response = redirect("account:unsubscribe_page")
        response["location"] += f"?email={email}"
        return response
    try:
        user = CustomUser.objects.get(username=username, email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid email or username.")
        response = redirect("account:unsubscribe_page")
        response["location"] += f"?email={email}"
        return response

    user.is_send_mail = False
    user.save()
    return redirect("account:unsubscribe_done_page")


# def get_subscription(request):
#     if request.method != "POST":
#         return JsonResponse({"status": False})
#
#     email = request.POST.get("addr")
#     username = request.POST.get("username")
#     if not email or not username:
#         return JsonResponse({"status": False})
#
#     try:
#         user = CustomUser.objects.get(username=username, email=email)
#     except CustomUser.DoesNotExist:
#         return JsonResponse({"status": False})
#
#     conditions = user.condition.all()
#     return JsonResponse({"status": True, "subscriptions": [{"id": s.id} for s in conditions]})

@require_GET
def get_gift(request):
    if not request.GET:
        return JsonResponse({"status": False})

    form = GiftFormSearch(request.GET, initial={"available": (0, "Any")})
    if not form.is_valid():
        return JsonResponse({"status": False, "errors": form.errors})

    gift_type = form.cleaned_data.get("gift_type")
    available = form.cleaned_data.get("available")
    dt_from = form.cleaned_data.get("dt_from")
    dt_to = form.cleaned_data.get("dt_to")
    fv_min = form.cleaned_data.get("face_value_min")
    fv_max = form.cleaned_data.get("face_value_max")
    price_min = form.cleaned_data.get("price_min")
    price_max = form.cleaned_data.get("price_max")
    rate_min = form.cleaned_data.get("rate_min")
    rate_max = form.cleaned_data.get("rate_max")

    limit = form.cleaned_data.get("limit")

    if available == "0":
        available = [True, False]
    elif available == "1":
        available = [True]
    elif available == "2":
        available = [False]
    # dt_from = timezone.make_aware(dt_from)
    # dt_to = timezone.make_aware(dt_to)

    qs = Gift.objects.filter(gift_type__name=gift_type, available__in=available, added_at__gte=dt_from,
                             added_at__lte=dt_to,
                             face_value__gte=fv_min, face_value__lte=fv_max, price__gte=price_min, price__lte=price_max,
                             rate__gte=rate_min, rate__lte=rate_max).order_by("added_at").reverse()[:limit]

    gifts = [{"face_value": x.face_value, "price": x.price, "rate": x.rate,
              "added_at": x.added_at.replace(second=0, microsecond=0).isoformat(),
              "sold_at": x.sold_at.replace(second=0, microsecond=0).isoformat() if x.sold_at else None} for x in qs]
    return JsonResponse({"status": True, "gifts": gifts})


def test(request):
    form = GiftFormSearch(request.GET)
    form.is_valid()
    return JsonResponse({"data": request.GET, "status": form.cleaned_data, "msg": form.errors})
