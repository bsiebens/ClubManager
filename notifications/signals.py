# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from generic_notifications.models import Notification
#
# from .consumers import send_notification_to_consumer
#
#
# # @receiver(post_save, sender=Notification)
# # def alert_new_notifications(instance, **kwargs) -> None:
# #     send_notification_to_consumer(instance.recipient)

from constance import config
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import strip_tags
from generic_notifications.models import Notification
from webpush import send_user_notification


@receiver(post_save, sender=Notification)
def send_web_push_notification(instance, created, **kwargs) -> None:
    url = config.CM_CLUB_URL
    head = f"ClubManager - {instance.subject}"
    icon = ""

    if config.CM_CLUB_NAME is not None or config.CM_CLUB_NAME != "":
        head = f"{config.CM_CLUB_NAME} - {instance.subject}"

    if config.CM_CLUB_LOGO is not None or config.CM_CLUB_LOGO != "":
        icon = f"{url}/static/{config.CM_CLUB_LOGO}"

    payload = {"head": head, "body": strip_tags(instance.text), "url": f"{url}{instance.get_absolute_url()}", "icon": icon}

    if created and not instance.is_read:
        send_user_notification(user=instance.recipient, payload=payload, ttl=1000)
