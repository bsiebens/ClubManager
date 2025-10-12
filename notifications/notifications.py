from generic_notifications.types import register, NotificationType


@register
class CalendarNotification(NotificationType):
    key: str = "calendar"
    name: str = "Calendar Notifications"
    description: str = "Notification for events, new event created or event updated."


@register
class RegistrationNotification(NotificationType):
    key: str = "registration"
    name: str = "Registration Notifications"
    description: str = "Notification for new registrations."


@register
class MessageNotification(NotificationType):
    key: str = "message"
    name: str = "Message Notifications"
    description: str = "Notification for new messages."
