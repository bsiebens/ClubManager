from django.http import HttpRequest
from generic_notifications.utils import get_unread_count


def unread_notification_count(request: HttpRequest) -> dict[str, int]:
    if request.user.is_anonymous:
        return {"unread_notification_count": 0}

    return {"unread_notification_count": get_unread_count(request.user)}
