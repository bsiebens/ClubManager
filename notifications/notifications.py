from generic_notifications.types import register, NotificationType


@register
class CalendarNotification(NotificationType):
    key: str = "calendar"
    name: str = "Calendar Notifications"
    description: str = "Notification for events, new event created or event updated."
