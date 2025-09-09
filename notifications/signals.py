import hashlib

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from generic_notifications.models import Notification


@receiver(post_save, sender=Notification)
def alert_new_notifications(instance, **kwargs) -> None:
    user = instance.recipient
    group_name = hashlib.md5(f"notifications_{user.id}_{user.email}".encode()).hexdigest()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(group_name, {"type": "update.icons"})
