from django.urls import path
from django.views.generic import RedirectView

from notifications import views as notifications_views
from . import views
from ..lib import do_redirect

app_name = "clubmanager"

urlpatterns2 = [
    path("", RedirectView.as_view(pattern_name="clubmanager:news")),
    path("news/", views.NewsView.as_view(), name="news"),
    path("calendar/", views.CalendarView.as_view(), name="calendar"),
    path("notifications/", views.NotificationsView.as_view(), name="notifications"),
    path("notifications/read/<int:notification_pk>/", views.NotificationsView.as_view(), name="notifications-read"),
    path("notifications/mark-all-read/", views.NotificationsView.as_view(), {"action": "mark-all-read"}, name="notifications-mark-all-read"),
    path("notifications/delete-all-read/", views.NotificationsView.as_view(), {"action": "delete-all-read"}, name="notifications-delete-all-read"),
    path("messages/", views.messages, name="messages"),
    path("settings/", views.settings, name="settings"),
]


urlpatterns = [
    path("", do_redirect, {"pattern_name": "clubmanager:news"}, name="index"),
    path("news/", views.news, name="news"),
    path("calendar/", views.calendar, name="calendar"),
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/<int:notification_pk>/", views.notifications, name="notifications-read"),
    path("notifications/mark-all-read/", views.notifications, {"mark_read": True}, name="notifications-mark-all-read"),
    path("notifications/delete-all-read/", views.notifications, {"delete_read": True}, name="notifications-delete-all-read"),
    path("notifications/check/", notifications_views.check_notifications, name="notifications-check"),
    path("messages/", views.messages, name="messages"),
    path("settings/", views.settings, name="settings"),
]
