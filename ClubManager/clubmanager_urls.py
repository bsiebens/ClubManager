from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "clubmanager"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="clubmanager:news")),
    path("news/", views.news, name="news"),
]
