from django.urls import path

from activities.feed import ActivityFeed
from . import views

app_name = "clubmanager"
urlpatterns = [
    path("", views.news, name="home"),
    path("news/", views.news, name="news"),
    path("calendar/", views.calendar, name="calendar"),
    path("calendar/update_registration/", views.update_registration, name="update_registration"),
    path('calendar/feed/', ActivityFeed(), name='activity_feed'),
    path("conversations/", views.conversations, name="conversations"),
    path("notifications/", views.notifications, name="notifications"),
    path("settings/", views.settings, name="settings"),
    path("check/", views.check, name="check"),
    path("sidebar/upcoming_activities/", views.sidebar_upcoming_activities, name="sidebar_upcoming_activities"),
]