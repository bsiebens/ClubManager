from django.urls import path
from members.backend import views

app_name = "members"

urlpatterns = [
    path("members", views.MemberListView.as_view(), name="members_list"),
]