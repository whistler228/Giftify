from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("/unsubscribe", views.unsubscribe, name="unsubscribe")
]
