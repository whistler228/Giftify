from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("unsubscribe", views.unsubscribe, name="unsubscribe"),
    path("gift", views.get_gift, name="get_gift"),
    # path("subscription", views.get_subscription, name="get_subscription")
]
