from django import forms
from django.utils import timezone

from core.models import GiftType, Gift


class GiftFormSearch(forms.Form):
    gift_type = forms.ChoiceField(
        choices=[(x.name, x.display_name) for x in GiftType.objects.all()],
        label="ギフト券")  # forms.CharField(max_length=16)
    available = forms.ChoiceField(
        choices=((0, "全て"), (1, "販売中"), (2, "取引済み"),),
        widget=forms.RadioSelect
    )
    available.widget.template_name = "core/widget/radio.html"
    available.widget.option_template_name = "core/widget/radio_options.html"

    limit = forms.ChoiceField(
        choices=((100, 100), (250, 250), (500, 500), (1000, 1000)),
        widget=forms.RadioSelect
    )
    limit.widget.template_name = "core/widget/radio.html"
    limit.widget.option_template_name = "core/widget/radio_options.html"

    face_value_min = forms.IntegerField(required=False, label="額面価格")
    face_value_max = forms.IntegerField(required=False, label="")
    price_min = forms.IntegerField(required=False, label="取引価格")
    price_max = forms.IntegerField(required=False, label="")
    rate_min = forms.FloatField(required=False, label="割引率")
    rate_max = forms.FloatField(required=False, label="")
    dt_from = forms.DateTimeField(required=False, label="期間")
    dt_to = forms.DateTimeField(required=False, label="")

    def __init__(self, *args, **kwargs):
        super(GiftFormSearch, self).__init__(*args, **kwargs)
        self.initial["available"] = 0
        self.initial["limit"] = 100

    def clean(self):
        cleaned_data = super(GiftFormSearch, self).clean()
        dt_from = cleaned_data.get("dt_from")
        dt_to = cleaned_data.get("dt_to")

        if dt_from > dt_to:
            cleaned_data["dt_from"] = dt_to
            cleaned_data["dt_to"] = dt_from

    def clean_gift_type(self):
        gift_type = self.cleaned_data["gift_type"]
        try:
            GiftType.objects.get(name=gift_type)
        except Exception:
            raise forms.ValidationError("Invalid Gift Type")
        return gift_type

    def clean_available(self):
        return self.cleaned_data["available"]

    def clean_face_value_min(self):
        data = self.cleaned_data["face_value_min"]
        if not data:
            data = 0
        return max(data, 0)

    def clean_face_value_max(self):
        data = self.cleaned_data["face_value_max"]
        if not data:
            data = 1000000
        return min(data, 1000000)

    def clean_price_min(self):
        data = self.cleaned_data["price_min"]
        if not data:
            data = 0
        return max(data, 0)

    def clean_price_max(self):
        data = self.cleaned_data["price_max"]
        if not data:
            data = 1000000
        return min(data, 1000000)

    def clean_rate_min(self):
        data = self.cleaned_data["rate_min"]
        if not data:
            data = 0.
        return max(data, 0.)

    def clean_rate_max(self):
        data = self.cleaned_data["rate_max"]
        if not data:
            data = 100.
        return min(data, 100.)

    def get_date_range(self):
        if Gift.objects.all().exists():
            oldest = Gift.objects.filter(gift_type__name=self.cleaned_data["gift_type"]) \
                .order_by("added_at").first().added_at
        else:
            oldest = timezone.make_aware(timezone.datetime.strptime("2020", "%Y"))
        latest = timezone.make_aware(timezone.datetime.now())
        return oldest, latest

    def clean_dt_from(self):  # oldest < dt < latest
        dt_from = self.cleaned_data["dt_from"]
        oldest, latest = self.get_date_range()

        if not dt_from:
            dt_from = oldest
        dt_from = max(dt_from, oldest)
        dt_from = min(dt_from, latest)
        return dt_from

    def clean_dt_to(self):  # oldest < dt < latest
        dt_to = self.cleaned_data["dt_to"]
        oldest, latest = self.get_date_range()

        if not dt_to:
            dt_to = latest
        dt_to = max(dt_to, oldest)
        dt_to = min(dt_to, latest)
        return dt_to

    def clean_limit(self):
        return int(self.cleaned_data["limit"])


class TestForm(forms.Form):
    interval = forms.ChoiceField(
        choices=((0, "DAY"), (1, "HOUR"), (2, "MINUTE"),),
        widget=forms.RadioSelect
    )
    interval.widget.template_name = "core/widget/radio.html"
    interval.widget.option_template_name = "core/widget/radio_options.html"
