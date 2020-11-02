from datetime import timedelta
from logging import getLogger

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Min
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

from account.models import CustomUser, Condition
from core.forms import GiftFormSearch
from core.models import Gift, GiftType

logger = getLogger(__name__)


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

class FormData:
    def __init__(self, cleaned_data):
        self.gift_type = cleaned_data.get("gift_type")
        self.available = cleaned_data.get("available")
        self.dt_from = cleaned_data.get("dt_from")
        self.dt_to = cleaned_data.get("dt_to")
        self.fv_min = cleaned_data.get("face_value_min")
        self.fv_max = cleaned_data.get("face_value_max")
        self.price_min = cleaned_data.get("price_min")
        self.price_max = cleaned_data.get("price_max")
        self.rate_min = cleaned_data.get("rate_min")
        self.rate_max = cleaned_data.get("rate_max")

        self.limit = cleaned_data.get("limit")

        if self.available == "0":
            self.available = [True, False]
        elif self.available == "1":
            self.available = [True]
        elif self.available == "2":
            self.available = [False]
        # dt_from = timezone.make_aware(dt_from)
        # dt_to = timezone.make_aware(dt_to)


@require_GET
def get_gift(request):
    form = GiftFormSearch(request.GET, initial={"available": (0, "Any")})
    if not form.is_valid():
        return JsonResponse({"status": False, "errors": form.errors})

    form_data = FormData(form.cleaned_data)

    qs = Gift.objects.filter(gift_type__name=form_data.gift_type, available__in=form_data.available,
                             added_at__gte=form_data.dt_from, added_at__lte=form_data.dt_to,
                             face_value__gte=form_data.fv_min, face_value__lte=form_data.fv_max,
                             price__gte=form_data.price_min, price__lte=form_data.price_max,
                             rate__gte=form_data.rate_min, rate__lte=form_data.rate_max) \
             .order_by("added_at").reverse()[:form_data.limit]

    gifts = [{"face_value": x.face_value, "price": x.price, "rate": x.rate,
              "added_at": x.added_at.replace(second=0, microsecond=0).isoformat(),
              "sold_at": x.sold_at.replace(second=0, microsecond=0).isoformat() if x.sold_at else None} for x in qs]
    gift_type = GiftType.objects.get(name=form_data.gift_type)
    return JsonResponse({"status": True, "giftType": gift_type.display_name, "data": gifts})


@require_GET
def get_periodic_data(request):
    form = GiftFormSearch(request.GET, initial={"available": (0, "Any")})
    if not form.is_valid():
        return JsonResponse({"status": False, "errors": form.errors})

    form_data = FormData(form.cleaned_data)
    days = (form_data.dt_to - form_data.dt_from).days

    res = []
    for i in range(days + 1):
        date = form_data.dt_from.date() + timedelta(days=i)
        gifts = Gift.objects.filter(
            gift_type__name=form_data.gift_type, available__in=form_data.available,
            added_at__gte=form_data.dt_from, added_at__lte=form_data.dt_to,
            face_value__gte=form_data.fv_min, face_value__lte=form_data.fv_max,
            price__gte=form_data.price_min, price__lte=form_data.price_max,
            rate__gte=form_data.rate_min, rate__lte=form_data.rate_max,
            added_at__date=date
        )

        if gifts:
            rate = gifts.aggregate(Avg("rate"), Min("rate"))

            res.append({"date": date, "stat": rate})

    gift_type = GiftType.objects.get(name=form_data.gift_type)
    return JsonResponse({"status": True, "giftType": gift_type.display_name, "data": res})


def test(request):
    form = GiftFormSearch(request.GET)
    form.is_valid()
    return JsonResponse({"data": request.GET, "status": form.cleaned_data, "msg": form.errors})


@login_required
@require_GET
def set_notification(request):
    form = GiftFormSearch(request.GET)
    if not form.is_valid() or not request.GET.get("action"):
        return JsonResponse({"status": False, "msg": form.errors})

    form_data = FormData(form.cleaned_data)
    gift_type = GiftType.objects.get(name=form_data.gift_type)
    cond, _ = Condition.objects.get_or_create(gift_type=gift_type, min_price=form_data.price_min,
                                              max_price=form_data.price_max, max_rate=form_data.rate_max)

    if request.GET.get("action") == "add":
        cond.user.add(request.user)
    elif request.GET.get("action") == "remove":
        cond.user.remove(request.user)

    if cond.user.filter(username=request.user.username).exists():
        return JsonResponse({"status": True, "msg": "registered"})
    else:
        if not cond.user.exists():
            cond.delete()
        return JsonResponse({"status": True, "msg": "unregistered"})
