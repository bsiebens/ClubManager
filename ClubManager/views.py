from collections import OrderedDict

from django.db.models import Q, Prefetch
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_htmx.http import HttpResponseClientRedirect
from generic_notifications.channels import WebsiteChannel
from generic_notifications.models import Notification
from generic_notifications.utils import mark_notifications_as_read, get_notifications

from activities.models import Activity, Practice, Registration
from members.models import Member
from teams.models import Season, Team


# from notifications.consumers import send_notification_to_consumer


def news(request: HttpRequest) -> HttpResponse:
    return render(request, "ClubManager/news.html", {})


def calendar(request: HttpRequest) -> HttpResponse:
    members = Member.objects.filter(Q(user=request.user) | Q(family_members__user=request.user)).distinct().values_list("id", flat=True)
    teams = Team.objects.filter(teammembership__season=Season.for_date(), teammembership__member__in=members).distinct().values_list("id", flat=True)

    activities = (
        Activity.objects.not_instance_of(Practice)
        .filter(Q(teams__in=teams) | Q(members__in=members))
        .filter(start_time__gte=timezone.now())
        .select_related("type")
        .prefetch_related(Prefetch("registrations", queryset=Registration.objects.filter(member__in=members).select_related("member", "member__user").order_by("member__user__last_name", "member__user__first_name"), to_attr="my_registrations"))
        .prefetch_related(Prefetch("registrations", queryset=Registration.objects.select_related("member", "member__user").order_by("member__user__last_name", "member__user__first_name"), to_attr="all_registrations"))
        .order_by("start_time")
    )

    # Materialize the queryset so we can post-process the prefetched data once
    activities = list(activities)

    # Wrap all_registrations in a list-like object that exposes grouped_by_response
    class _RegistrationList(list):
        def __init__(self, iterable):
            super().__init__(iterable)
            # Buckets similar to RegistrationManager.grouped_by_response default
            buckets = OrderedDict(
                [
                    (_("attending"), {Registration.ResponseOptions.ATTENDING}),
                    (_("selected"), {Registration.ResponseOptions.SELECTED}),
                    (_("not selected"), {Registration.ResponseOptions.NOT_SELECTED}),
                    (_("not attending"), {Registration.ResponseOptions.NOT_ATTENDING}),
                    (_("no response"), {Registration.ResponseOptions.NO_RESPONSE}),
                ]
            )
            response_to_bucket = {status: bucket_name for bucket_name, statuses in buckets.items() for status in statuses}
            grouped = OrderedDict((bucket_name, []) for bucket_name in buckets.keys())

            for r in self:
                bucket_name = response_to_bucket.get(r.response)
                if bucket_name is not None:
                    grouped[bucket_name].append(r)

            # Order inside buckets by member's last and first names
            for bucket_list in grouped.values():
                bucket_list.sort(
                    key=lambda r: (
                        (getattr(r.member.user, "last_name", "") or "").lower(),
                        (getattr(r.member.user, "first_name", "") or "").lower(),
                    )
                )

            # Expose to templates as expected
            self.grouped_by_response = grouped

    for activity in activities:
        # Ensure the attribute exists (it should due to prefetch), then wrap
        if hasattr(activity, "all_registrations") and isinstance(activity.all_registrations, list):
            activity.all_registrations = _RegistrationList(activity.all_registrations)

    return render(request, "ClubManager/calendar.html", {"activities": activities})


def update_registration(request: HttpRequest) -> HttpResponse:
    registration_id, registration_response = request.POST.get("response_button").split("|")
    registration = Registration.objects.get(id=registration_id)

    # Verify if we have access to this registration
    if registration.member.user == request.user or registration.member in request.user.member.family_members.all():
        registration.response = registration_response
        registration.save(update_fields=["response"])

    buckets = OrderedDict(
        [
            (_("attending"), {Registration.ResponseOptions.ATTENDING}),
            (_("selected"), {Registration.ResponseOptions.SELECTED}),
            (_("not selected"), {Registration.ResponseOptions.NOT_SELECTED}),
            (_("not attending"), {Registration.ResponseOptions.NOT_ATTENDING}),
            (_("no response"), {Registration.ResponseOptions.NO_RESPONSE}),
        ]
    )

    activity = registration.activity
    all_registrations = activity.registrations.grouped_by_response(buckets=buckets)

    return render(request, "ClubManager/registration_update.html", {"registration": registration, "activity": activity, "all_registrations": all_registrations})


def notifications(request: HttpRequest, notification_id: int | None = None, mark_all_read: bool = False, delete_read: bool = False) -> HttpResponse:
    template_name = "ClubManager/notifications.html"
    if request.htmx:
        template_name += "#list"

    if mark_all_read:
        mark_notifications_as_read(request.user)
        # send_notification_to_consumer(request.user)

    if notification_id is not None:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read()

        return HttpResponseClientRedirect(notification.get_absolute_url())

    if delete_read:
        request.user.notifications.filter(read__isnull=False).delete()

    notifications_for_user = get_notifications(user=request.user, channel=WebsiteChannel)

    return render(request, template_name, {"notifications": notifications_for_user})
