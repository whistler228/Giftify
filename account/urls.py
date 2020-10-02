from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    path("signup", views.SignUp.as_view(), name="signup"),
    path("detail", views.user_detail, name="user_detail"),
    path("unsubscribe", views.unsubscribe, name="unsubscribe_page")
]
