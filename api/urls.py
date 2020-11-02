from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("unsubscribe", views.unsubscribe, name="unsubscribe"),
    path("gift", views.get_gift, name="get_gift"),
    path("stat", views.get_periodic_data, name="get_periodic_data"),
    path("notify", views.set_notification, name="set_notification"),
    path("test", views.test, name="test"),
    # path("subscription", views.get_subscription, name="get_subscription")
]
