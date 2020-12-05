from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from .forms import CustomUserCreateForm, UnsubscribeForm, CustomUserUpdateForm
from .models import CustomUser


class SignUp(generic.CreateView):
    form_class = CustomUserCreateForm
    success_url = reverse_lazy("login")
    template_name = "account/signup.html"


@login_required
def user_detail(request):
    user = get_object_or_404(CustomUser, username=request.user.username)
    return render(request, "account/detail.html", {"nickname": user.nickname})


def unsubscribe(request):
    email = request.GET.get("email", None)
    form = UnsubscribeForm(initial={"email": email})
    if email:
        form.fields["email"].widget.attrs["readonly"] = True
    return render(request, "account/unsubscribe_form.html", {"email": email, "form": form})


def unsubscribe_done(request):
    return render(request, "account/unsubscribe_done.html")
