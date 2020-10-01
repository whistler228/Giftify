from huey import crontab
from huey.contrib.djhuey import periodic_task

from collect.views import collect_from_api
from core.models import GiftType


@periodic_task(crontab(minute="*/1"))
def periodic_get_data():
    gift_types = GiftType.objects.all()
    for gift_type in gift_types:
        collect_from_api(gift_type.name)
