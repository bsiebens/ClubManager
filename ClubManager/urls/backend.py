from .. import views
from .. import configuration

from django.urls import path, include

app_name = "backend"
urlpatterns = [
    path("", views.index, name="index"),
    path("members/", include("members.backend.urls")),
    path("configuration/", configuration.index, name="configuration"),
]