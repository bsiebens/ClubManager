from django.db.models import Q, Prefetch
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from generic_notifications.channels import WebsiteChannel
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
        .order_by("start_time")
    )

    return render(request, "ClubManager/calendar.html", {"activities": activities})


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
