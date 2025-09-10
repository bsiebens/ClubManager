from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from generic_notifications.channels import WebsiteChannel
from generic_notifications.utils import mark_notifications_as_read, get_notifications

# from notifications.consumers import send_notification_to_consumer


def news(request: HttpRequest) -> HttpResponse:
    return render(request, "ClubManager/news.html", {})


def notifications(request: HttpRequest, mark_read: bool = False, delete_read: bool = False) -> HttpResponse:
    template_name = "ClubManager/notifications.html"
    if request.htmx:
        template_name += "#list"

    if mark_read:
        mark_notifications_as_read(request.user)
        # send_notification_to_consumer(request.user)

    if delete_read:
        request.user.notifications.filter(read__isnull=False).delete()

    notifications_for_user = get_notifications(user=request.user, channel=WebsiteChannel)

    return render(request, template_name, {"notifications": notifications_for_user})
