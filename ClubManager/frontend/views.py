from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from generic_notifications.channels import WebsiteChannel
from generic_notifications.utils import get_notifications, mark_notifications_as_read

from activities.models import Activity, Practice, Registration, grouped_by_response
from members.models import Member
from teams.models import Team, Season
from ..lib import AlpineTemplateResponse, is_alpine


@login_required
def news(request: HttpRequest) -> HttpResponse:
    return render(request, "ClubManager/news.html", {})


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
                    return AlpineTemplateResponse(request, "ClubManager/calendar_not_attending.html", {"registration": registration})

                else:
                    registration.response = response
                    registration.save(update_fields=["response"])

            activity = registration.activity
            all_registrations = grouped_by_response(activity.registrations.all(), buckets, order_inside_bucket=True)

            context.update({"activity": activity, "registration": registration, "all_registrations": all_registrations})

            if not is_alpine(request):
                return redirect("clubmanager:calendar")

        else:
            members = Member.objects.filter(Q(user=request.user) | Q(family_members__user=request.user)).distinct().values_list("pk", flat=True)
            teams = Team.objects.filter(teammembership__season=Season.for_date(), teammembership__member__in=members).distinct().values_list("pk", flat=True)
            activities = (
                Activity.objects.not_instance_of(Practice)
                .filter(Q(teams__in=teams) | Q(members__in=members))
                .filter(start_time__gte=timezone.now())
                .select_related("type")
                .prefetch_related(
                    Prefetch("registrations", queryset=Registration.objects.filter(member__in=members).select_related("member", "member__user").order_by("member__user__last_name", "member__user__first_name"), to_attr="my_registrations")
                )
                .prefetch_related(Prefetch("registrations", queryset=Registration.objects.select_related("member", "member__user").order_by("member__user__last_name", "member__user__first_name"), to_attr="all_registrations"))
                .order_by("start_time")
            )

            activities = list(activities)
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
