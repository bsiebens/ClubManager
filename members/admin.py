# Register your models here.
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Member

admin.site.register(Member, SimpleHistoryAdmin)
