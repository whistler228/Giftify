from django import forms

from account.models import CustomUser


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
