import hashlib

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth.models import AbstractUser
from django.template.loader import render_to_string
from generic_notifications.channels import WebsiteChannel
from generic_notifications.utils import get_unread_count


def send_notification_to_consumer(user: AbstractUser) -> None:
    if not user.is_anonymous:
        group_name = hashlib.md5(f"notifications_{user.id}_{user.email}".encode()).hexdigest()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, {"type": "update.icons"})


class NotificationConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_name = None

    def connect(self):
        user = self.scope["user"]

        if user.is_authenticated:
            self.group_name = hashlib.md5(f"notifications_{user.id}_{user.email}".encode()).hexdigest()
            async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
            self.accept()

        else:
            self.close()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def update_icons(self, event):
        unread_notifications = get_unread_count(user=self.scope["user"], channel=WebsiteChannel)
        template = render_to_string("notifications/notification.html", {"unread_notifications": unread_notifications > 0})

        self.send(text_data=template)
