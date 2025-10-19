from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django_htmx.http import trigger_client_event

from activities.models import Registration, Activity, grouped_by_response
from django.utils.translation import gettext_lazy as _
from collections import OrderedDict
from django.db.models import Q
from django.utils import timezone

from frontend.utils import HTMXTemplateResponse
from members.models import Member
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
    partial_template = "news"
    page_number = request.GET.get("page", 1)
    
    if page_number != 1:
        partial_template = "news_items"

    news_items = NewsItem.objects.filter(status=NewsItem.StatusChoices.RELEASED, publish_on__lte=timezone.now()).filter(Q(type=NewsItem.NewsItemTypeChoices.INTERNAL) | Q(type=NewsItem.NewsItemTypeChoices.INTERNAL_EXTERNAL)).order_by("-created")
    paginator = Paginator(news_items, 10)
    page = paginator.get_page(page_number)
    
    return HTMXTemplateResponse(request, "ClubManager/frontend/news.html", {"page": page}, partial_template)

def calendar(request: HttpRequest) -> HttpResponse:
    activities = Activity.for_user(request.user, include_registrations=True)
    
    # Make sure activities are populated before grouping responses
    activities = list(activities)
    for activity in activities:
        if hasattr(activity, "all_registrations") and isinstance(activity.all_registrations, list):
            activity.all_registrations = grouped_by_response(activity.all_registrations, BUCKETS, order_inside_bucket=True)
            
    return HTMXTemplateResponse(request, "ClubManager/frontend/calendar.html", {"activities": activities}, partial_template="calendar")

@login_required
@require_POST
def update_registration(request: HttpRequest) -> HttpResponse:
    activity = Activity.objects.get(pk=request.POST.get("activity_pk"))
    member = Member.objects.get(pk=request.POST.get("member_pk"))
    
    if request.POST.get("response") == "not_attending":
        comment = request.POST.get("comment", "")
        registration = activity.registrations.get(member=member)
        
        if comment == "" or comment is None:
            if not request.htmx:
                return render(request, "ClubManager/frontend/calendar_comment_form.html", {"activity": activity, "member": member, "htmx": False})
            
            return HTMXTemplateResponse(request, "ClubManager/frontend/calendar.html", {"activity": activity, "member": member, "registration": registration, "htmx": True}, partial_template="registration_comment_modal")
            
        else:
            registration = Activity.update_registration_status_for_member(activity, member, request.user, request.POST.get("response"), comment)
            all_registrations = grouped_by_response(activity.registrations.all(), BUCKETS, order_inside_bucket=True)
            
            if not request.htmx:
                return redirect("clubmanager:calendar")
            
            response = HTMXTemplateResponse(request, "ClubManager/frontend/calendar.html", {"activity": activity, "registration": registration, "all_registrations": all_registrations, "swap": True}, partial_template="registration_update")
            return trigger_client_event(response, "registrationsUpdated")
    
    else:
        registration = Activity.update_registration_status_for_member(activity, member, request.user, request.POST.get("response"), request.POST.get("comment", ""))
        all_registrations = grouped_by_response(activity.registrations.all(), BUCKETS, order_inside_bucket=True)
        
        if not request.htmx:
            return redirect("clubmanager:calendar")

        response = HTMXTemplateResponse(request, "ClubManager/frontend/calendar.html", {"activity": activity, "registration": registration, "all_registrations": all_registrations, "swap": True}, partial_template="registration_update")
        return trigger_client_event(response, "registrationsUpdated")

def conversations(request: HttpRequest) -> HttpResponse: ...

def notifications(request: HttpRequest) -> HttpResponse: ...

def settings(request: HttpRequest) -> HttpResponse: ...

def check(request: HttpRequest) -> HttpResponse:
    return render(request, "ClubManager/base.html#icons")

def sidebar_upcoming_activities(request: HttpRequest) -> HttpResponse:
    activities = Activity.for_user(request.user, include_registrations=True).filter(start_time__gte=timezone.now()).order_by("start_time")[:5]
    
    return render(request, "ClubManager/frontend/sidebar/upcoming_activities.html", {"activities": activities})