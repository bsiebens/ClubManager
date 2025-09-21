# Register your models here.
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Opponent, Competition, Activity, ActivityType, Game, Event, Practice, PracticeOccurrence, Registration

admin.site.register(Opponent)
admin.site.register(Competition)
admin.site.register(Activity)
admin.site.register(ActivityType)
admin.site.register(Game)
admin.site.register(Event)
admin.site.register(Practice)
admin.site.register(PracticeOccurrence)
admin.site.register(Registration, SimpleHistoryAdmin)
