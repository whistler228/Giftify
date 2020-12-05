from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import CharField

from account.models import CustomUser


class CustomUserCreateForm(UserCreationForm):
    email = CharField(required=True, max_length=254, label="E-Mail address")
    nickname = CharField(required=True, max_length=12, label="Nickname")

    class Meta:
        model = CustomUser
        fields = ("username", "nickname", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(CustomUserCreateForm, self).save(commit=False)
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


class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("nickname", "email")


class UnsubscribeForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(max_length=150)

    def clean(self):
        cleaned_data = super(UnsubscribeForm, self).clean()
        try:
            user = CustomUser.objects.get(username=self.username, email=self.email)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError(
                "メールアドレスまたはユーザー名が間違っています"
            )
