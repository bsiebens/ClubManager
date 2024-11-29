#  Copyright (c) ClubManager - Bernard Siebens 2024.

from django.urls import path

from . import views

app_name = "teams"

urlpatterns = [
    path("seasons", views.SeasonListView.as_view(), name="seasons_list"),
    path("seasons/add", views.SeasonAddView.as_view(), name="seasons_add"),
    path("seasons/delete/<int:pk>", views.SeasonDeleteView.as_view(), name="seasons_delete"),
    path("teamroles", views.TeamRoleListView.as_view(), name="teamroles_list"),
    path("teamroles/add", views.TeamRoleAddView.as_view(), name="teamroles_add"),
    path("teamroles/edit/<int:pk>", views.TeamRoleEditView.as_view(), name="teamroles_edit"),
    path("teamroles/delete/<int:pk>", views.TeamRoleDeleteView.as_view(), name="teamroles_delete"),
    path("numberpools", views.NumberPoolListView.as_view(), name="numberpools_list"),
    path("numberpools/add", views.NumberPoolAddView.as_view(), name="numberpools_add"),
    path("numberpools/delete/<int:pk>", views.NumberPoolDeleteView.as_view(), name="numberpools_delete"),
    path("teams", views.TeamListView.as_view(), name="teams_list"),
    path("teams/add", views.TeamAddView.as_view(), name="teams_add"),
    path("teams/edit/<int:pk>", views.TeamEditView.as_view(), name="teams_edit"),
    path("teams/delete/<int:pk>", views.TeamDeleteView.as_view(), name="teams_delete"),
]
