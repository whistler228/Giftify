from django.db import models


class Gift(models.Model):
    gift_id = models.IntegerField(primary_key=True)
    face_value = models.IntegerField()
    price = models.IntegerField()
    rate = models.FloatField()
    gift_type = models.ForeignKey("GiftType", on_delete=models.CASCADE, related_name="gift_type")
    available = models.BooleanField()

    added_at = models.DateTimeField()
    sold_at = models.DateTimeField(null=True)


class GiftType(models.Model):
    name = models.CharField(max_length=16, unique=True)
    display_name = models.CharField(max_length=16)

    def __str__(self):
        return self.name
