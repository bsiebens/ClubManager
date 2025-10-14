from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from ClubManager.lib import HTMXTemplateResponse
from news.models import NewsItem


@login_required
def news(request: HttpRequest) -> HttpResponse:
    news_items = NewsItem.objects.filter(status=NewsItem.StatusChoices.RELEASED, publish_on__lte=timezone.now()).filter(Q(type=NewsItem.NewsItemTypeChoices.INTERNAL) | Q(type=NewsItem.NewsItemTypeChoices.INTERNAL_EXTERNAL)).order_by("-created")
    partial_template = "news" if request.GET.get("page", 1) == 1 else "news_items"

    paginator = Paginator(news_items, 10)
    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)

    return HTMXTemplateResponse(request, "ClubManager/frontend/news.html", {"page": page}, partial_template=partial_template)


def calendar(request: HttpRequest) -> HttpResponse:
    return HTMXTemplateResponse(request, "ClubManager/frontend/calendar.html", {}, partial_template="calendar")


def conversations(request: HttpRequest) -> HttpResponse: ...


def notifications(request: HttpRequest) -> HttpResponse: ...


def settings(request: HttpRequest) -> HttpResponse: ...


@login_required
def check(request: HttpRequest) -> HttpResponse:
    return render(request, "ClubManager/base.html#icons")
