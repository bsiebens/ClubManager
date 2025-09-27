# Register your models here.
from django.contrib import admin

from .models import NewsItem, Attachment

admin.site.register(NewsItem)
admin.site.register(Attachment)
