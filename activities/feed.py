from constance import config
from django.conf import settings
from django.http import Http404
from django_ical.views import ICalFeed

from activities.models import Activity, ActivityType
from members.models import Member


class ActivityFeed(ICalFeed):
    product_id = "-//ClubManager//Activity Feed//EN"
    timezone = settings.TIME_ZONE
    filename = "activities.ics"

    URL = config.CM_CLUB_URL + "/clubmanager/calendar/"

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)

    def items(self, user):
        token = self.request.GET.get("token")

        try:
            member = Member.objects.get(token=token)
        except Member.DoesNotExist:
            raise Http404("Invalid token")

        return Activity.for_user(user=member.user)

    def item_title(self, item):
        if item.type.type == ActivityType.ActivityTypes.GAME:
            if item.opponent:
                return f"{item.team.name} vs. {item.opponent}"
            else:
                return f"Game {item.team}"

        else:
            return f"{', '.join([team.name for team in item.teams.all()])} - {item.get_title()}"

    def item_description(self, item):
        return item.description

    def item_start_datetime(self, item):
        return item.start_time

    def item_end_datetime(self, item):
        return item.end_time

    def item_link(self, item):
        return self.URL

    def item_guid(self, item):
        return f"{item.pk}global_name"

    def item_location(self, item):
        return item.location
