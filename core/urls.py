from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("", views.top, name="top_page"),
    path("<slug:gift_type>/", views.plot, name="plot_gift"),
]
