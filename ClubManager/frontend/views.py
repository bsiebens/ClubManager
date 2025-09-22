from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from generic_notifications.channels import WebsiteChannel
from generic_notifications.utils import get_notifications, mark_notifications_as_read

from activities.models import Activity, Practice, Registration
from members.models import Member
from teams.models import Team, Season
from ..lib import AlpineTemplateResponse


@login_required
def news(request: HttpRequest) -> HttpResponse:
    return render(request, "ClubManager/news.html", {})


@login_required
def calendar(request: HttpRequest) -> HttpResponse: ...


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

    return AlpineTemplateResponse(request, "ClubManager/notifications.html", {"notifications": notifications_for_user})


@login_required
def messages(request: HttpRequest) -> HttpResponse: ...


@login_required
def settings(request: HttpRequest) -> HttpResponse: ...


class NewsView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs) -> TemplateResponse:
        return TemplateResponse(request, "ClubManager/news.html")


class CalendarView(LoginRequiredMixin, View):
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

    def get(self, request: HttpRequest, *args, **kwargs) -> TemplateResponse:
        members = Member.objects.filter(Q(user=request.user) | Q(family_members__user=request.user)).distinct().values_list("pk", flat=True)
        teams = Team.objects.filter(teammembership__season=Season.for_date(), teammembership__member__in=members).distinct().values_list("pk", flat=True)
        activities = (
            Activity.objects.not_instance_of(Practice)
            .filter(Q(teams__in=teams) | Q(members__in=members))
            .filter(start_time__gte=timezone.now())
            .select_related("type")
            .prefetch_related(Prefetch("registrations", queryset=Registration.objects.filter(member__in=members).select_related("member", "member__user").order_by("member__user__last_name", "member__user__first_name"), to_attr="my_registrations"))
            .prefetch_related(Prefetch("registrations", queryset=Registration.objects.select_related("member", "member__user").order_by("member__user__last_name", "member__user__first_name"), to_attr="all_registrations"))
            .order_by("start_time")
        )

        # Trigger queryset evaluation
        activities = list(activities)

        for activity in activities:
            if hasattr(activity, "all_registrations") and isinstance(activity.all_registrations, list):
                activity.all_registrations = self._RegistrationList(activity.all_registrations)

        return TemplateResponse(request, "ClubManager/calendar.html", {"activities": activities})

    def post(self, request: HttpRequest, *ars, **kwargs) -> HttpResponseRedirect:
        registration = get_object_or_404(Registration, pk=request.POST.get("registration_pk"))
        response = request.POST.get("registration_response")

        # Verify if we have access to the registration
        if registration.member.user == request.user or registration.member in request.user.member.family_members.all():
            registration.response = response
            registration.save(update_fields=["response"])

        return redirect("clubmanager:calendar")


class NotificationsView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, notification_pk: int | None = None, *args, **kwargs) -> TemplateResponse | HttpResponseRedirect:
        if notification_pk is not None:
            notification = get_object_or_404(request.user.notifications, pk=notification_pk)
            notification.mark_as_read()

            return redirect(notification.get_absolute_url())

        notifications = get_notifications(user=request.user, channel=WebsiteChannel)

        return TemplateResponse(request, "ClubManager/notifications.html", {"notifications": notifications})

    def post(self, request: HttpRequest, action: str | None = None, *args, **kwargs) -> HttpResponseRedirect:
        match action:
            case "mark-all-read":
                mark_notifications_as_read(request.user)
            case "delete-all-read":
                request.user.notifications.filter(read__isnull=False).delete()
            case _:
                pass

        return redirect("clubmanager:notifications")
