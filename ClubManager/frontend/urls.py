from django.urls import path

from messaging import views as messaging_views
from notifications import views as notifications_views
from . import views
from ..lib import do_redirect

app_name = "clubmanager"

urlpatterns = [
    path("", do_redirect, {"pattern_name": "clubmanager:news"}, name="index"),
    path("news/", views.news, name="news"),
    path("calendar/", views.calendar, name="calendar"),
    path("calendar/<int:registration_pk>/<str:response>/", views.calendar, name="calendar-update-response"),
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/<int:notification_pk>/", views.notifications, name="notifications-read"),
    path("notifications/mark-all-read/", views.notifications, {"mark_read": True}, name="notifications-mark-all-read"),
    path("notifications/delete-all-read/", views.notifications, {"delete_read": True}, name="notifications-delete-all-read"),
    path("notifications/check/", notifications_views.check_notifications, name="notifications-check"),
    path("chat/", views.chat, name="messages"),
    path("chat/<int:conversation_pk>/", views.chat, name="messages-conversation"),
    path("chat/check/", messaging_views.check_messages, name="messages-check"),
    path("chat/add/", messaging_views.add_message, name="messages-add"),
    path("settings/", views.settings, name="settings"),
]
