import hashlib

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.template.loader import render_to_string
from generic_notifications.channels import WebsiteChannel
from generic_notifications.utils import get_unread_count


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
        print(unread_notifications)
        template = render_to_string("notifications/notification.html", {"unread_notifications": unread_notifications > 0})

        self.send(text_data=template)
