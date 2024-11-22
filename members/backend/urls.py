from django.urls import path
from members.backend import views

app_name = "members"

urlpatterns = [
    path("members", views.MemberListView.as_view(), name="members_list"),
    path("members/add", views.MemberAddView.as_view(), name="members_add"),
]