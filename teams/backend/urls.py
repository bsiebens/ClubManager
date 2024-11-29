#  Copyright (c) ClubManager - Bernard Siebens 2024.

from django.urls import path

from . import views

app_name = "teams"

urlpatterns = [
    path("seasons", views.SeasonListView.as_view(), name="seasons_list"),
    path("seasons/add", views.SeasonAddView.as_view(), name="seasons_add"),
    path("seasons/delete/<int:pk>", views.SeasonDeleteView.as_view(), name="seasons_delete"),
    path("teamrole", views.TeamRoleListView.as_view(), name="teamroles_list"),
    path("teamrole/add", views.TeamRoleAddView.as_view(), name="teamroles_add"),
    path("teamrole/edit/<int:pk>", views.TeamRoleEditView.as_view(), name="teamroles_edit"),
    path("teamrole/delete/<int:pk>", views.TeamRoleDeleteView.as_view(), name="teamroles_delete"),
]
