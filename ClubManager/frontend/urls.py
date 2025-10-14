from django.urls import path

from . import views
from ..lib import do_redirect

app_name = "clubmanager"
urlpatterns = [
    path("", do_redirect, {"pattern_name": "clubmanager:news"}, name="index"),
    path("news/", views.news, name="news"),
    path("calendar/", views.calendar, name="calendar"),
    path("conversations/", views.conversations, name="conversations"),
    path("notifications/", views.notifications, name="notifications"),
    path("settings/", views.settings, name="settings"),
    path("check/", views.check, name="check"),
]
