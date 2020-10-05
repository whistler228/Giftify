from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

from account.models import CustomUser


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
