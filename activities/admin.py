# Register your models here.
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Opponent, Competition, Activity, ActivityType, Game, Event, Practice, PracticeOccurrence, Registration

admin.site.register(Opponent)
admin.site.register(Competition)
admin.site.register(Activity)
admin.site.register(ActivityType)
admin.site.register(Game, SimpleHistoryAdmin)
admin.site.register(Event, SimpleHistoryAdmin)
admin.site.register(Practice, SimpleHistoryAdmin)
admin.site.register(PracticeOccurrence, SimpleHistoryAdmin)
admin.site.register(Registration, SimpleHistoryAdmin)
