from django.http import Http404
from django_ical.views import ICalFeed
from activities.models import Activity
from django.conf import settings

from members.models import Member
from constance import config

class ActivityFeed(ICalFeed):
    product_id ='-//ClubManager//Activity Feed//EN'
    timezone = settings.TIME_ZONE

    URL = config.CM_CLUB_URL + "calendar/"

    def get_object(self, request, *args, **kwargs):
        token = request.GET.get('token')
        
        try:
            member = Member.objects.get(token=token)
            return member.user
        except Member.DoesNotExist:
            raise Http404("Invalid token")
    
    def items(self, user):
        items = Activity.for_user(user)
        print(items)
        
        return items
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.description
    
    def item_start_datetime(self, item):
        return item.start_time
    
    def item_end_datetime(self, item):
        return item.end_time
    
    def item_link(self, item):
        return self.URL
