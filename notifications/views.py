from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from generic_notifications.channels import WebsiteChannel
from generic_notifications.utils import get_unread_count


def check_notifications(request: HttpRequest) -> HttpResponse:
    unread_notifications = get_unread_count(user=request.user, channel=WebsiteChannel)

    return render(request, "notifications/notification.html", {"unread_notifications": unread_notifications > 0})
