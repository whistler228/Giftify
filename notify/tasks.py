from logging import getLogger

import sendgrid
from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from huey import crontab
from huey.contrib.djhuey import periodic_task, task
from sendgrid.helpers.mail import Mail, From, To
from webpush import send_user_notification

from account.models import CustomUser, Condition
from core.models import Gift, GiftType

logger = getLogger(__name__)


@periodic_task(crontab(minute="*/1"))
def periodic_check_condition():
    for condition in Condition.objects.all():
        res = check_condition(condition)
        if res.exists():
            for user in condition.user.all():
                id_list = res.values_list("gift_id", flat=True)
                if user.email and user.is_send_mail:
                    task_send_mail(
                        id_list,
                        condition.gift_type.name,
                        condition.id,
                        user.username
                    )
                task_send_webpush(
                    id_list,
                    condition.gift_type.name,
                    condition.id,
                    user.username
                )
                [user.notified.add(x) for x in res]


@task()
def task_send_mail(_gift_ids, _gift_type, _condition_id, username):
    return send_mail(_gift_ids, _gift_type, _condition_id, username)


@task()
def task_send_webpush(_gift_ids, _gift_type, _condition_id, username):
    user = CustomUser.objects.get(username=username)
    for _gift_id in _gift_ids:
        send_webpush(user, _gift_id)
    logger.debug(f"[NOTIFY] Sent a Notification to {user.username}")


def send_mail(_gift_ids, _gift_type, _condition_id, username):
    user = CustomUser.objects.get(username=username)
    tz = timezone.pytz.timezone(user.timezone)
    gifts = [Gift.objects.get(gift_id=x) for x in _gift_ids]
    gift_type_id = _gift_type
    gift_type_name = GiftType.objects.get(name=_gift_type).display_name
    dist = user.email

    msg = Mail(
        From(settings.MAIL_ADDR),
        To(dist)
    )
    msg.dynamic_template_data = {
        "gift_type": gift_type_name,
        "gifts": [{"added_at": x.added_at.astimezone(tz).strftime("%Y/%m/%d-%H:%M:%S"),
                   "face_value": x.face_value,
                   "price": x.price} for x in gifts],
        "subject": "Amaten 出品のお知らせ",
        "image": "http://giftify.dplab.biz" + static(f"images/gift_logo/{gift_type_id}.png"),
        "amaten_url": f"https://amaten.com/exhibitions/{gift_type_id}",
        "unsubscribe": f"http://giftify.dplab.biz{reverse('account:unsubscribe_page')}?email={dist}&c={_condition_id}"
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


def send_webpush(user, gift_id):
    gift = Gift.objects.get(gift_id=gift_id)
    payload = {
        "head": f"{gift.gift_type.display_name} ギフト券出品通知",
        "body": f"額面:{gift.face_value}円 {gift.rate}%",
        "icon": f"https://giftify.dplab.biz{static('images/favicon/android-icon-192x192.png')}",
        "url": f"https://amaten.com/exhibitions/{gift.gift_type.name}"
    }
    send_user_notification(user=user, payload=payload, ttl=1000)


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
