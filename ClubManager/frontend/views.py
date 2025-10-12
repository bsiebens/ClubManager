from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch, Count, Case, When, Value, BooleanField
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from generic_notifications.channels import WebsiteChannel
from generic_notifications.utils import get_notifications, mark_notifications_as_read

from activities.models import Activity, Registration, grouped_by_response
from messaging.models import Conversation, Message, ConversationParticipant
from news.models import NewsItem
from ..lib import AlpineTemplateResponse, is_alpine


@login_required
def news(request: HttpRequest) -> HttpResponse:
    news_items = NewsItem.objects.filter(status=NewsItem.StatusChoices.RELEASED, publish_on__lte=timezone.now()).filter(Q(type=NewsItem.NewsItemTypeChoices.INTERNAL) | Q(type=NewsItem.NewsItemTypeChoices.INTERNAL_EXTERNAL)).order_by("-created")
    paginator = Paginator(news_items, 10)

    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)

    return AlpineTemplateResponse(request, "ClubManager/news.html", {"page": page, "is_alpine": is_alpine(request)}, partial_template="news")


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
def conversations(request: HttpRequest, conversation_pk: int | None = None) -> HttpResponse:
    conversations_for_user = Conversation.objects.for_user(request.user).with_unread_count(request.user).with_last_message().order_by("-last_message_time").prefetch_related("participants", "participants__user")
    conversation_set = True
    selected_conversation = None

    if conversation_pk is None:
        conversation_pk = conversations_for_user.first().pk if conversations.count() > 0 else None
        conversation_set = False

    if conversation_pk is not None:
        selected_conversation = Conversation.objects.prefetch_related(
            Prefetch("participants", queryset=ConversationParticipant.objects.filter(is_active=True).select_related("user")),
            Prefetch(
                "messages",
                queryset=Message.objects.filter(is_deleted=False)
                .select_related("sender")
                .annotate(
                    total_recipients=Count("readstatus"),
                    read_count=Count("readstatus", filter=Q(readstatus__read_at__isnull=False)),
                    read_by_all=Case(When(total_recipients__gt=0, read_count=Count("readstatus"), then=Value(True)), default=Value(False), output_field=BooleanField()),
                )
                .order_by("sent_at"),
            ),
        ).get(pk=conversation_pk)

    # Only mark as read if:
    # 1. On desktop (non-Alpine) and a conversation was explicitly selected, OR
    # 2. On mobile (Alpine) and specifically requesting to mark as read (e.g., when switching to chat view)
    should_mark_read = False
    if not is_alpine(request):
        # Desktop: mark as read when conversation is set (user clicked on it)
        should_mark_read = conversation_set
    else:
        # Mobile: only mark as read when explicitly requested (e.g., via a parameter or when viewing chat)
        should_mark_read = request.GET.get("mark_read", "false").lower() == "true"

    if should_mark_read:
        unread_messages = selected_conversation.messages.unread_for_user(request.user)
        for message in unread_messages:
            message.mark_as_read_by(request.user)

    return AlpineTemplateResponse(
        request,
        "ClubManager/conversations.html",
        {"conversations": conversations_for_user, "conversation_pk": conversation_pk, "selected_conversation": selected_conversation, "conversation_set": conversation_set},
        partial_template="messages_update",
    )


@login_required
def settings(request: HttpRequest) -> HttpResponse: ...
