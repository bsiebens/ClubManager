from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def check_notifications(request: HttpRequest) -> HttpResponse:
    return render(request, "ClubManager/base.html#notification_icon")
