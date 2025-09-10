from django.db.models.signals import post_save
from django.dispatch import receiver
from generic_notifications.models import Notification

from .consumers import send_notification_to_consumer


@receiver(post_save, sender=Notification)
def alert_new_notifications(instance, **kwargs) -> None:
    send_notification_to_consumer(instance.recipient)
