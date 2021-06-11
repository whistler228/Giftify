from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    path("signup", views.SignUp.as_view(), name="signup"),
    path("detail", views.user_detail, name="user_detail"),
    path("setting", views.setting, name="setting"),
    path("notifications", views.notifications, name="notifications"),
    path("unsubscribe", views.unsubscribe, name="unsubscribe_page"),
    path("unsubscribed", views.unsubscribe_done, name="unsubscribe_done_page")
]
