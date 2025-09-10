from django.urls import path
from django.views.generic import RedirectView

from notifications import views as notifications_views
from . import views

app_name = "clubmanager"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="clubmanager:news")),
    path("news/", views.news, name="news"),
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/mark-read/", views.notifications, {"mark_read": True}, name="notifications-mark-read"),
    path("notifications/delete-read/", views.notifications, {"delete_read": True}, name="notifications-delete-read"),
    path("notifications/check/", notifications_views.check_notifications, name="notifications-check"),
]
