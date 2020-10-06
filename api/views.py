from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_GET

from account.models import CustomUser
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
    data = request.GET
    gift_type = data.get("type")
    available = False if data.get("available", "true") != "true" else True
    dt_from = data.get("from", timezone.datetime.strptime("2000-1-1", "%Y-%m-%d"))
    dt_to = data.get("to", timezone.datetime.strptime("2100-1-1", "%Y-%m-%d"))
    fv_min = int(data.get("faceValueMin", 0))
    fv_max = int(data.get("faceValueMax", 1000000))
    price_min = int(data.get("priceMin", 0))
    price_max = int(data.get("priceMax", 1000000))
    rate_min = int(data.get("rateMin", 0.))
    rate_max = int(data.get("rateMax", 100.))

    dt_from = timezone.make_aware(dt_from)
    dt_to = timezone.make_aware(dt_to)

    if not gift_type:
        return JsonResponse({"status": False})

    qs = Gift.objects.filter(gift_type__name=gift_type, available=available, added_at__gte=dt_from, added_at__lte=dt_to,
                             face_value__gte=fv_min, face_value__lte=fv_max, price__gte=price_min, price__lte=price_max,
                             rate__gte=rate_min, rate__lte=rate_max)

    gifts = [{"face_value": x.face_value, "price": x.price, "rate": x.rate, "added_at": x.added_at.isoformat()} for x in
             qs]
    return JsonResponse({"status": True, "gifts": gifts})
