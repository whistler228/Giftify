from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import CharField
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from .models import CustomUser


class CustomForm(UserCreationForm):
    email = CharField(required=True, max_length=254, label="E-Mail address")
    nickname = CharField(required=True, max_length=12, label="Nickname")

    class Meta:
        model = CustomUser
        fields = ("username", "nickname", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(CustomForm, self).save(commit=False)
        user.nickname = self.cleaned_data["nickname"]
        if commit:
            user.save()
        return user

    def clean_nickname(self):
        if not self.cleaned_data["nickname"]:
            raise ValidationError("Please Enter your nickname.")
        if len(self.cleaned_data["nickname"]) > 12:
            raise ValidationError("Nickname must be <= 12 char.")
        return self.cleaned_data["nickname"]


class SignUp(generic.CreateView):
    form_class = CustomForm
    success_url = reverse_lazy("login")
    template_name = "account/signup.html"


@login_required
def user_detail(request):
    user = get_object_or_404(CustomUser, username=request.user.username)
    return render(request, "account/detail.html", {"nickname": user.nickname})


def unsubscribe(request):
    return None
