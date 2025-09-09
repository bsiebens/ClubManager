from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def check_unread_count(request: HttpRequest, request_item: str) -> HttpResponse:
    return HttpResponse(0)


def news(request: HttpRequest) -> HttpResponse:
    return render(request, "ClubManager/news.html", {})
