import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from django.conf import settings
from django.template.loader import render_to_string
from django.test import TestCase

from account.models import CustomUser
from core.models import GiftType, Gift

logger = logging.getLogger(__name__)


class SendMailTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SendMailTest, cls).setUpClass()
        cls.user = CustomUser.objects.create(username="test_user", email="kadonoboti1@gmail.com", password="1234")
        gift_type = GiftType.objects.create(name="google_play")
        cls.gift = Gift.objects.create(gift_id=1, face_value=10000, price=8200, rate=82.0, gift_type=gift_type,
                                       available=True)
        cls.gift = Gift.objects.create(gift_id=2, face_value=10000, price=8300, rate=83.0, gift_type=gift_type,
                                       available=True)

    def test_sendmail(self):
        r = send_mail([self.gift.gift_id], self.user.username)
        return self.assertTrue(r)


def send_mail(_gift_ids, username):
    user = CustomUser.objects.get(username=username)
    gifts = [Gift.objects.get(gift_id=x) for x in _gift_ids]

    def create_msg():
        return render_to_string("notify/mail_body.html", {"user": user, "gifts": gifts})

    try:
        smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10, context=ssl.create_default_context())
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
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPConnectError) as e:
        logger.error(e)
        print(e)
    logger.debug(f"[NOTIFY] Sent a Mail to {user.email}")
    return True
