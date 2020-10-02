from django.http import JsonResponse

from account.models import CustomUser


def unsubscribe(request):
    if request.method != "GET":
        return JsonResponse({"status": False})

    email = request.GET.get("addr")
    username = request.GET.get("username")
    if not email or not username:
        return JsonResponse({"status": False})
    user = CustomUser.objects.get(username=username, email=email)
