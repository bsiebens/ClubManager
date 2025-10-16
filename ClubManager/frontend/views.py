from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ClubManager.lib import HTMXTemplateResponse
from activities.models import Registration, Activity, grouped_by_response
from news.models import NewsItem

BUCKETS = OrderedDict(
    [
        (_("attending"), {Registration.ResponseOptions.ATTENDING}),
        (_("selected"), {Registration.ResponseOptions.SELECTED}),
        (_("not selected"), {Registration.ResponseOptions.NOT_SELECTED}),
        (_("not attending"), {Registration.ResponseOptions.NOT_ATTENDING}),
        (_("no response"), {Registration.ResponseOptions.NO_RESPONSE}),
    ]
)


@login_required
def news(request: HttpRequest) -> HttpResponse:
    news_items = NewsItem.objects.filter(status=NewsItem.StatusChoices.RELEASED, publish_on__lte=timezone.now()).filter(Q(type=NewsItem.NewsItemTypeChoices.INTERNAL) | Q(type=NewsItem.NewsItemTypeChoices.INTERNAL_EXTERNAL)).order_by("-created")
    partial_template = "news" if request.GET.get("page", 1) == 1 else "news_items"

    paginator = Paginator(news_items, 10)
    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)

    return HTMXTemplateResponse(request, "ClubManager/frontend/news.html", {"page": page}, partial_template=partial_template)


def calendar(request: HttpRequest) -> HttpResponse:
    context = {}

    if request.method == "POST":
        ...

    else:
        number_of_items = request.GET.get("limit", None)

        activities = Activity.for_user(request.user, include_registrations=True)

        if number_of_items is not None:
            activities = activities[: int(number_of_items)]

        # Making sure the activities list is populated before grouping the responses
        activities = list(activities)
        for activity in activities:
            if hasattr(activity, "all_registrations") and isinstance(activity.all_registrations, list):
                activity.all_registrations = grouped_by_response(activity.all_registrations, BUCKETS, order_inside_bucket=True)

        context.update({"activities": activities})

    return HTMXTemplateResponse(request, "ClubManager/frontend/calendar.html", context=context, partial_template="calendar")


def conversations(request: HttpRequest) -> HttpResponse: ...


def notifications(request: HttpRequest) -> HttpResponse: ...


def settings(request: HttpRequest) -> HttpResponse: ...


@login_required
def check(request: HttpRequest) -> HttpResponse:
    return render(request, "ClubManager/base.html#icons")
