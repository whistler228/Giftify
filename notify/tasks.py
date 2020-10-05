from logging import getLogger

import pytz
import sendgrid
from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from huey import crontab
from huey.contrib.djhuey import periodic_task, task
from sendgrid.helpers.mail import Mail, From, To

from account.models import CustomUser, Condition
from core.models import Gift

logger = getLogger(__name__)


@periodic_task(crontab(minute="*/1"))
def periodic_check_condition():
    for condition in Condition.objects.all():
        res = check_condition(condition)
        if res.exists():
            for user in condition.user.all():
                if user.email and user.is_send_mail:
                    task_send_mail(
                        res.values_list("gift_id", flat=True),
                        user.username
                    )
                [user.notified.add(x) for x in res]


@task()
def task_send_mail(_gift_ids, _condition_id, username):
    return send_mail(_gift_ids, _condition_id, username)


def send_mail(_gift_ids, _condition_id, username):
    user = CustomUser.objects.get(username=username)
    tz = pytz.timezone(user.timezone)
    gifts = [Gift.objects.get(gift_id=x) for x in _gift_ids]
    dist = user.email

    msg = Mail(
        From(settings.MAIL_ADDR),
        To(dist)
    )
    msg.dynamic_template_data = {
        "gifts": [{"added_at": x.added_at.astimezone(tz).strftime("%Y/%m/%d-%H:%M:%S"),
                   "face_value": x.face_value,
                   "price": x.price} for x in gifts],
        "subject": "Amaten 出品のお知らせ",
        "image": "http://amaten.dplab.biz" + static("images/gift_logo/google_play.png"),
        "unsubscribe": f"http://amaten.dplab.biz{reverse('account:unsubscribe_page')}?email={dist}&c={_condition_id}"
    }
    msg.template_id = "d-7f2de4cff2554542ace60013acff23d5"
    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API)
        response = sg.send(msg.get())
    except Exception as e:
        logger.error(e)
        print(e)
        return None
    logger.debug(f"[NOTIFY] Sent a Mail to {user.email}")
    return dist


def check_condition(condition):
    res = Gift.objects.filter(gift_type=condition.gift_type, available=True) \
        .exclude(notified_users__in=condition.user.all())
    if condition.min_price:
        res = res.filter(price__gte=condition.min_price)
    if condition.max_price:
        res = res.filter(price__lte=condition.max_price)
    if condition.max_rate:
        res = res.filter(rate__lte=condition.max_rate)

    return res
