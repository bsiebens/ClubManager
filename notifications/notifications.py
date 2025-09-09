from generic_notifications.types import register, NotificationType


@register
class EventNotification(NotificationType):
    key: str = "event"
    name: str = "Event Notifications"
    description: str = "Notification for events, new event created or event updated."
