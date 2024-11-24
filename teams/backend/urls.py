#  Copyright (c) ClubManager - Bernard Siebens 2024.

from django.urls import path

from . import views

app_name = "teams"

urlpatterns = [
    path("seasons", views.SeasonListView.as_view(), name="seasons_list"),
    path("seasons/add", views.SeasonAddView.as_view(), name="seasons_add"),
]
