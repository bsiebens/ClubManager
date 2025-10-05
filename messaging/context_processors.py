from django.http import HttpRequest

from messaging.models import Message


def unread_messages_count(request: HttpRequest) -> dict[str, int]:
    if request.user.is_anonymous:
        return {"unread_messages_count": 0}

    return {"unread_messages_count": Message.objects.unread_for_user(request.user).count()}
