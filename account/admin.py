from django.contrib import admin

from account.models import CustomUser, Condition

admin.site.register(CustomUser)
admin.site.register(Condition)
