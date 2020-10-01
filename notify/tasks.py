import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from logging import getLogger

from django.conf import settings
from django.template.loader import render_to_string
from huey import crontab
from huey.contrib.djhuey import periodic_task, task

from account.models import CustomUser, Condition
from core.models import Gift

logger = getLogger(__name__)


@periodic_task(crontab(minute="*/1"))
def check_condition():
    for condition in Condition.objects.all():
        res = Gift.objects.filter(gift_type=condition.gift_type, available=True) \
            .exclude(notified_users__in=[condition.user])
        if condition.min_price:
            res = res.filter(price__gte=condition.min_price)
        if condition.max_price:
            res = res.filter(price__lte=condition.max_price)
        if condition.max_rate:
            res = res.filter(rate__lte=condition.max_rate)
        if res.exists():
            if condition.user.email:
                send_mail(
                    res.values_list("gift_id", flat=True),
                    condition.user.username
                )
            [condition.user.notified.add(x) for x in res]


@task()
def send_mail(_gift_ids, username):
    user = CustomUser.objects.get(username=username)
    gifts = [Gift.objects.get(gift_id=x) for x in _gift_ids]

    def create_msg():
        return render_to_string("notify/mail_body.html",
                                {"user": user, "gifts": gifts, "gift_type": gifts[0].gift_type.name})

    try:
        smtp = smtplib.SMTP_SSL("smtp.yandex.com", 465, timeout=10, context=ssl.create_default_context())
        smtp.login(settings.MAIL_ADDR, settings.MAIL_PASS)
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "ギフト券が出品されました"
        msg["From"] = settings.MAIL_ADDR
        msg["To"] = user.email
        msg["Date"] = formatdate()
        plain_part = MIMEText("text", "plain")
        html_part = MIMEText(create_msg(), "html")
        msg.attach(plain_part)
        msg.attach(html_part)
        smtp.sendmail(settings.MAIL_ADDR, user.email, msg.as_string())
        smtp.close()
    except [smtplib.SMTPAuthenticationError, smtplib.SMTPConnectError] as e:
        logger.error(e)
        print(e)
    logger.debug(f"[NOTIFY] Sent a Mail to {user.email}")
    return True
