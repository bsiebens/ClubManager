from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def check_notifications(request: HttpRequest) -> HttpResponse:
    return render(request, "ClubManager/base.html#notification_icon")
