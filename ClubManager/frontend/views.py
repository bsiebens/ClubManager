from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from generic_notifications.channels import WebsiteChannel
from generic_notifications.utils import get_notifications, mark_notifications_as_read

from activities.models import Activity, Registration, grouped_by_response
from news.models import NewsItem
from ..lib import AlpineTemplateResponse, is_alpine


@login_required
def news(request: HttpRequest) -> HttpResponse:
    news_items = NewsItem.objects.filter(status=NewsItem.StatusChoices.RELEASED, publish_on__lte=timezone.now()).filter(Q(type=NewsItem.NewsItemTypeChoices.INTERNAL) | Q(type=NewsItem.NewsItemTypeChoices.INTERNAL_EXTERNAL)).order_by("-created")[:5]

    return render(request, "ClubManager/news.html", {"news_items": news_items})


@login_required
def calendar(request: HttpRequest, registration_pk: int | None = None, response: str | None = None) -> HttpResponse | HttpResponseRedirect:
    buckets = OrderedDict(
        [
            (_("attending"), {Registration.ResponseOptions.ATTENDING}),
            (_("selected"), {Registration.ResponseOptions.SELECTED}),
            (_("not selected"), {Registration.ResponseOptions.NOT_SELECTED}),
            (_("not attending"), {Registration.ResponseOptions.NOT_ATTENDING}),
            (_("no response"), {Registration.ResponseOptions.NO_RESPONSE}),
        ]
    )
    context = {}

    if request.method == "POST":
        registration = get_object_or_404(Registration, pk=request.POST.get("registration_pk"))

        if registration.member.user == request.user or registration.member in request.user.member.family_members.all():
            registration.response = request.POST.get("response")
            registration.comment = request.POST.get("comment")
            registration.save(update_fields=["response", "comment"])

            activity = registration.activity
            all_registrations = grouped_by_response(activity.registrations.all(), buckets, order_inside_bucket=True)

            context.update({"activity": activity, "registration": registration, "all_registrations": all_registrations})

        if not is_alpine(request):
            return redirect("clubmanager:calendar")

    else:
        if registration_pk is not None and response in ["attending", "not_attending", "no_response"]:
            registration = get_object_or_404(Registration, pk=registration_pk)

            # Verify if we have access to the registration
            if registration.member.user == request.user or registration.member in request.user.member.family_members.all():
                if response == "not_attending" and not is_alpine(request):
                    return AlpineTemplateResponse(request, "ClubManager/calendar_comment_form.html", {"registration": registration})

                else:
                    registration.response = response
                    registration.save(update_fields=["response"])

            activity = registration.activity
            all_registrations = grouped_by_response(activity.registrations.all(), buckets, order_inside_bucket=True)

            context.update({"activity": activity, "registration": registration, "all_registrations": all_registrations})

            if not is_alpine(request):
                return redirect("clubmanager:calendar")

        else:
            activities = list(Activity.for_user(request.user, include_registrations=True))
            for activity in activities:
                # Ensure the attribute exists (it should due to prefetch), then wrap
                if hasattr(activity, "all_registrations") and isinstance(activity.all_registrations, list):
                    activity.all_registrations = grouped_by_response(activity.all_registrations, buckets, order_inside_bucket=True)

            context.update({"activities": activities})

    return AlpineTemplateResponse(request, "ClubManager/calendar.html", context, partial_template="registration_update")


@login_required
def notifications(request: HttpRequest, notification_pk: int | None = None, mark_read: bool = False, delete_read: bool = False) -> HttpResponse | HttpResponseRedirect:
    if notification_pk is not None:
        notification = get_object_or_404(request.user.notifications, pk=notification_pk)
        notification.mark_as_read()

        return redirect(notification.get_absolute_url())

    if mark_read:
        mark_notifications_as_read(request.user)

    if delete_read:
        request.user.notifications.filter(read__isnull=False).delete()

    notifications_for_user = get_notifications(user=request.user, channel=WebsiteChannel)

    return AlpineTemplateResponse(request, "ClubManager/notifications.html", {"notifications": notifications_for_user}, partial_template="notification_update")


@login_required
def chat(request: HttpRequest) -> HttpResponse: ...


@login_required
def settings(request: HttpRequest) -> HttpResponse: ...
